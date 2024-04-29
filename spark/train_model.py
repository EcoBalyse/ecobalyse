from pyspark.sql import SparkSession
import os
from mongo_module import Mongo
from pyspark.sql.functions import expr,col, count, lit, rand, sum, when
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType
import mlflow
import mlflow.spark
from pyspark.ml.feature import Imputer, StringIndexer, StandardScaler, VectorAssembler, OneHotEncoder, IndexToString, VectorIndexer
from pyspark.ml.linalg import DenseVector
from pyspark.ml.regression import RandomForestRegressor, LinearRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator, RegressionEvaluator
from pyspark.sql import functions as F
from pyspark.sql.functions import stddev, lit

# Create uri

uri = f"mongodb+srv://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0"
# MLFLOW

mlflow.set_tracking_uri(uri="http://mlflow:5000")
mlflow.set_experiment(experiment_name='ecobalyse_dst')

# Create Spark
spark = SparkSession.builder \
    .appName("MongoDB Spark Connector Example") \
    .config("spark.mongodb.input.uri", uri) \
    .config("spark.mongodb.output.uri", uri) \
    .config("spark.mongodb.input.database", "ecobalyse") \
    .config("spark.mongodb.input.collection", "countries") \
    .config("spark.mongodb.input.collection", "materials") \
    .config("spark.mongodb.input.collection", "products") \
    .config("spark.mongodb.input.collection", "fabricProcess") \
    .config("spark.mongodb.input.collection", "products_details") \
    .config("spark.mongodb.input.collection", "impacts_documentation") \
    .config("spark.mongodb.input.collection", "impacts") \
    .config("spark.mongodb.output.database", "ecobalyse") \
    .config("spark.mongodb.output.collection", "countries") \
    .config("spark.mongodb.output.collection", "materials") \
    .config("spark.mongodb.output.collection", "products") \
    .config("spark.mongodb.output.collection", "fabricProcess") \
    .config("spark.mongodb.output.collection", "products_details") \
    .config("spark.mongodb.output.collection", "impacts_documentation") \
    .config("spark.mongodb.output.collection", "impacts") \
    .getOrCreate()

# Load data collections into Spark DataFrames and store them into Spark dfs

collections = ["countries", "materials", "products", "fabricProcess", "products_details", "impacts", "impacts_documentation"]
dfs = {}

for collection in collections:
    df = spark.read.format("mongo").option("collection", collection).load()
    dfs[collection] = df

# Define new schema to rename nested fields impact names

struct_schema = StructType([
    StructField("acd", DoubleType()),
    StructField("cch", DoubleType()),
    StructField("etf", IntegerType()),
    StructField("etf_c", DoubleType()),
    StructField("fru", DoubleType()),
    StructField("fwe", DoubleType()),
    StructField("htc", IntegerType()),
    StructField("htc_c", DoubleType()),
    StructField("htn", IntegerType()),
    StructField("htn_c", DoubleType()),
    StructField("ior", DoubleType()),
    StructField("ldu", DoubleType()),
    StructField("mru", DoubleType()),
    StructField("ozd", DoubleType()),
    StructField("pco", DoubleType()),
    StructField("pma", DoubleType()),
    StructField("swe", DoubleType()),
    StructField("tre", DoubleType()),
    StructField("wtu", DoubleType()),
    StructField("ecs", DoubleType()),
    StructField("pef", DoubleType())
])
dfs['impacts'] = dfs['impacts'].withColumn("impacts", col("impacts").cast(struct_schema))
dfs = dfs['impacts']

# Delete columns _id, md5_id, etc.
dfs = dfs.drop("_id", "md5_id","transport", "complementsImpacts","durability","useNbCycles","daysOfWear", "lifeCycle")
dfs.show(20)

# Keep only the ecs value in the impacts column
df_vf = dfs.withColumn("impacts", col("impacts").getItem("ecs"))

# Display the resulting DataFrame
df_vf.show()
df_vf.printSchema()

# Select the required columns and rename the column names

selected_df = df_vf.select(col("impacts").alias("ImpactScore"),
    col("product_id").alias("ProductId"),
    F.expr("transform(inputs.materials, x -> x.material.id)").alias("MaterialsIds"),
    F.expr("transform(inputs.materials, x -> x.share)").alias("MaterialsShares"),
    col("inputs.countryDyeing.code").alias("CountryDyeingCode"),
    col("inputs.countryFabric.code").alias("CountryFabricCode"),
    col("inputs.countryMaking.code").alias("CountryMakingCode"),
    col("inputs.fabricProcess").alias("FabricProcess"),
    col("inputs.mass").alias("Mass"),
    col("inputs.airTransportRatio").alias("AirTransportRatio"))


selected_df = selected_df.select(
    col("ImpactScore"),
    col("ProductId"),
    col("MaterialsIds")[0].alias("MaterialId_1"),
    col("MaterialsIds")[1].alias("MaterialId_2"),
    col("MaterialsShares")[0].alias("MaterialId_1_share"),
    col("MaterialsShares")[1].alias("MaterialId_2_share"),
    col("CountryDyeingCode"),
    col("CountryFabricCode"),
    col("CountryMakingCode"),
    col("FabricProcess"),
    col("Mass"),
    col("AirTransportRatio"),
    )


selected_df = selected_df.drop("Price")
selected_df.show()
selected_df.describe().toPandas()

# Display missing values

# Count the number of missing values in each column

missing_counts = selected_df.select([sum(when(col(c).isNull(), 1).otherwise(0)).alias(c) for c in selected_df.columns]) \
                             .collect()[0]

# Display the number of missing values for each column
for col_name, missing_count in zip(selected_df.columns, missing_counts):
    print(f"Number of missing values in column '{col_name}': {missing_count}")

# Handling missing values

# Delete rows with missing values in the 'ProductId' column
selected_df = selected_df.na.drop(subset=["ProductId"])

# Replace missing values in the 'MaterialId_2' column with “no-material2”.
selected_df = selected_df.fillna("no-material2", subset=["MaterialId_2"])

# Replace missing values in the 'MaterialId_2_share' column with 0
selected_df = selected_df.fillna(0, subset=["MaterialId_2_share"])

# Replace missing values in the 'AirTransportRatio' column with the median
median_air_transport_ratio = selected_df.approxQuantile("AirTransportRatio", [0.5], 0.25)[0]
selected_df = selected_df.fillna(median_air_transport_ratio, subset=["AirTransportRatio"])

# Display the first 5 lines to check for changes
selected_df.show(5)

# Check for missing values in selected columns
selected_df.select([count(when(col(c).isNull(), c)).alias(c) for c in selected_df.columns]).show()

#-------------------------------#

# Creating indexers

CountryDyeingCodeIndexer = StringIndexer(inputCol='CountryDyeingCode', outputCol='indexedCountryDyeingCode')
CountryFabricCodeIndexer = StringIndexer(inputCol='CountryFabricCode', outputCol='indexedCountryFabricCode')
CountryMakingCodeIndexer = StringIndexer(inputCol='CountryMakingCode', outputCol='indexedCountryMakingCode')
FabricProcessIndexer = StringIndexer(inputCol='FabricProcess', outputCol='indexedFabricProcess')
MaterialId_1Indexer = StringIndexer(inputCol='MaterialId_1', outputCol='indexedMaterialId_1')
MaterialId_2Indexer = StringIndexer(inputCol='MaterialId_2', outputCol='indexedMaterialId_2')
ProductIdIndexer = StringIndexer(inputCol='ProductId', outputCol='indexedProductId')

# Combining treatments

all_stages = [
    CountryDyeingCodeIndexer,
    CountryFabricCodeIndexer,
    CountryMakingCodeIndexer,
    FabricProcessIndexer,
    MaterialId_1Indexer,
    MaterialId_2Indexer,
    ProductIdIndexer,
]

# Creating a Pipeline
pipeline = Pipeline(stages=all_stages)

# Index selected_df variables
dfIndexed = pipeline.fit(selected_df).transform(selected_df)

# Display an extract of hrIndexed
dfIndexed.sample(False, 0.001 , seed = 222).toPandas()

# Formatting the database in svmlib format #

# Create a database excluding non-indexed variables
dfNumeric = dfIndexed.select(
    'ImpactScore',
    'indexedProductId',
    'Mass',
    'indexedMaterialId_1',
    'indexedMaterialId_2',
    'MaterialId_1_share',
    'MaterialId_2_share',
    'indexedCountryDyeingCode',
    'indexedCountryFabricCode',
    'indexedCountryMakingCode',
    'indexedFabricProcess',
    'AirTransportRatio')

# Creation of a DenseVector variable containing features via the RDD structure
dfRdd = dfNumeric.rdd.map(lambda x: (x[0], DenseVector(x[1:])))

# DataFrame transformation and variable naming to obtain a database in svmlib format
dfLibsvm = spark.createDataFrame(dfRdd, ['label', 'features'])

# Displaying an extract from hrLibsvm
dfLibsvm.sample(False, .001, seed = 222).toPandas()
dfNumeric.describe().toPandas()

mlflow.autolog()

with mlflow.start_run(run_name="Ecobalyse test Linear Regression"):
    # Create a vector indexer to index the numeric columns in the “features” column
    featureIndexer = VectorIndexer(inputCol="features", outputCol="indexedFeatures", maxCategories=10).fit(dfLibsvm)

    # Create a RandomForest regressor
    lr = LinearRegression(featuresCol="features", labelCol="label")

    # Create pipeline with steps: featureIndexer, RandomForest
    pipeline_lr = Pipeline(stages=[featureIndexer] + [lr])

    # Decomposition of data into two sets: training and test data
    (train, test) = dfLibsvm.randomSplit([0.7, 0.3], seed = 222)

    # Model learning using training data
    model = pipeline_lr.fit(train)

    # Makes predictions about the test set
    predictions = model.transform(test)

    # Evaluates model performance
    evaluator = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
    rmse = evaluator.evaluate(predictions)
    print("Root Mean Squared Error (RMSE) on test data = %g" % rmse)

    # Calculate the standard deviation of the target variable
    target_stddev = test.select(stddev("label")).collect()[0][0]
    print("Standard deviation of target variable :", target_stddev)
    mlflow.spark.log_model(model, "spark-model-lr")

#-------- Random Forest setup

with mlflow.start_run(run_name="Ecobalyse test Random Forest"):
    # Creation of the Random Forest Regression estimator
    rf = RandomForestRegressor(featuresCol="features", labelCol="label")

    # Pipeline creation with feature indexer
    pipeline_rf = Pipeline(stages=[featureIndexer, rf])

    # Model training
    model_rf = pipeline_rf.fit(train)

    # Make predictions on test data
    predictions_rf = model_rf.transform(test)

    # Model evaluation by calculating RMSE
    rmse_rf = evaluator.evaluate(predictions_rf)
    print("Root Mean Squared Error (RMSE) with Random Forest Regression:", rmse_rf)

    # Calculation of the standard deviation of the target variable in the test data
    target_stddev_rf = test.select(stddev("label")).collect()[0][0]
    print("Standard deviation of target variable :", target_stddev_rf)
    mlflow.spark.log_model(model, "spark-model-rf")


#-------- Setting up the Dummy Regressor

with mlflow.start_run(run_name="Ecobalyse test Dummy Regressor"):
    # Calculate the mean of the target variable in the test data
    mean_target = train.selectExpr("avg(label)").collect()[0][0]

    # Create a DataFrame with a column of constant predictions based on the mean of the target variable
    predictions_dummy = test.withColumn("prediction", lit(mean_target))

    # Calculate RMSE
    rmse_dummy = evaluator.evaluate(predictions_dummy)
    print("Root Mean Squared Error (RMSE) with DummyRegressor:", rmse_dummy)

    # Calculate the standard deviation of the target variable in the test data
    target_stddev = test.select(stddev("label")).collect()[0][0]
    print("Standard deviation of target variable :", target_stddev)
    mlflow.spark.log_model(model, "spark-model-dr")

# Stop Spark session
spark.stop()
