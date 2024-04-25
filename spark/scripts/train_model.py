from dotenv import load_dotenv
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

load_dotenv()

# Create uri

uri = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0"
# MLFLOW

mlflow.set_tracking_uri(uri="http://mlflow-tracker:5000")
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

# Supprimer les colonnes _id, md5_id, etc.
dfs = dfs.drop("_id", "md5_id","transport", "complementsImpacts","durability","useNbCycles","daysOfWear", "lifeCycle")
dfs.show(20)

# Garder seulement la valeur ecs dans la colonne impacts
df_vf = dfs.withColumn("impacts", col("impacts").getItem("ecs"))

# Afficher le DataFrame résultant
df_vf.show()
df_vf.printSchema()

# sélectionner les colonnes nécessaires et renommer le nom des colonnes

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

#afficher les valeurs manquantes

# Compter le nombre de valeurs manquantes dans chaque colonne

missing_counts = selected_df.select([sum(when(col(c).isNull(), 1).otherwise(0)).alias(c) for c in selected_df.columns]) \
                             .collect()[0]

# Afficher le nombre de valeurs manquantes pour chaque colonne
for col_name, missing_count in zip(selected_df.columns, missing_counts):
    print(f"Nombre de valeurs manquantes dans la colonne '{col_name}': {missing_count}")

#traitement des valeurs manquantes

# Supprimer les lignes avec des valeurs manquantes dans la colonne 'ProductId'
selected_df = selected_df.na.drop(subset=["ProductId"])
# Remplacer les valeurs manquantes dans la colonne 'MaterialId_2' par "no-material2"
selected_df = selected_df.fillna("no-material2", subset=["MaterialId_2"])
# Remplacer les valeurs manquantes dans la colonne 'MaterialId_2_share' par 0
selected_df = selected_df.fillna(0, subset=["MaterialId_2_share"])
# Remplacer les valeurs manquantes dans la colonne 'AirTransportRatio' par la médiane
median_air_transport_ratio = selected_df.approxQuantile("AirTransportRatio", [0.5], 0.25)[0]
selected_df = selected_df.fillna(median_air_transport_ratio, subset=["AirTransportRatio"])
# Afficher les 5 premières lignes pour vérifier les changements
selected_df.show(5)
# Vérifier s'il reste des valeurs manquantes dans les colonnes sélectionnées
selected_df.select([count(when(col(c).isNull(), c)).alias(c) for c in selected_df.columns]).show()

#-------------------------------#



# Création des indexeurs

CountryDyeingCodeIndexer = StringIndexer(inputCol='CountryDyeingCode', outputCol='indexedCountryDyeingCode')
CountryFabricCodeIndexer = StringIndexer(inputCol='CountryFabricCode', outputCol='indexedCountryFabricCode')
CountryMakingCodeIndexer = StringIndexer(inputCol='CountryMakingCode', outputCol='indexedCountryMakingCode')
FabricProcessIndexer = StringIndexer(inputCol='FabricProcess', outputCol='indexedFabricProcess')
MaterialId_1Indexer = StringIndexer(inputCol='MaterialId_1', outputCol='indexedMaterialId_1')
MaterialId_2Indexer = StringIndexer(inputCol='MaterialId_2', outputCol='indexedMaterialId_2')
ProductIdIndexer = StringIndexer(inputCol='ProductId', outputCol='indexedProductId')

# Combiner les traitements

all_stages = [
    CountryDyeingCodeIndexer,
    CountryFabricCodeIndexer,
    CountryMakingCodeIndexer,
    FabricProcessIndexer,
    MaterialId_1Indexer,
    MaterialId_2Indexer,
    ProductIdIndexer,
]

# Création d'une Pipeline
pipeline = Pipeline(stages=all_stages)

# Indexer les variables de selected_df
dfIndexed = pipeline.fit(selected_df).transform(selected_df)

# Affichage d'un extrait de hrIndexed
dfIndexed.sample(False, 0.001 , seed = 222).toPandas()

# Mise en forme de la base en format svmlib #

# Création d'une base de données excluant les variables non indexées
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

# Création d'une variable DenseVector contenant les features en passant par la structure RDD
dfRdd = dfNumeric.rdd.map(lambda x: (x[0], DenseVector(x[1:])))

# Transformation en DataFrame et nommage des variables pour obtenir une base au format svmlib
dfLibsvm = spark.createDataFrame(dfRdd, ['label', 'features'])

# Affichage d'un extrait de hrLibsvm
dfLibsvm.sample(False, .001, seed = 222).toPandas()
dfNumeric.describe().toPandas()

mlflow.autolog()

with mlflow.start_run(run_name="Ecobalyse test Linear Regression"):
    # Créer un indexeur de vecteur pour indexer les colonnes numériques dans la colonne "features"
    featureIndexer = VectorIndexer(inputCol="features", outputCol="indexedFeatures", maxCategories=10).fit(dfLibsvm)
    # Créer un regressor RandomForest
    lr = LinearRegression(featuresCol="features", labelCol="label")

    # Créer le pipeline avec les étapes: featureIndexer, RandomForest
    pipeline_lr = Pipeline(stages=[featureIndexer] + [lr])

    # Décomposition des données en deux ensembles: données d'entraînement et de test
    (train, test) = dfLibsvm.randomSplit([0.7, 0.3], seed = 222)

    # Apprentissage du modèle en utilisant les données d'entraînement
    model = pipeline_lr.fit(train)

    # Fait des prédictions sur l'ensemble de test
    predictions = model.transform(test)

    # Évalue les performances du modèle
    evaluator = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
    rmse = evaluator.evaluate(predictions)
    print("Root Mean Squared Error (RMSE) on test data = %g" % rmse)

    # Calculer l'écart type de la variable cible
    target_stddev = test.select(stddev("label")).collect()[0][0]
    print("Écart type de la variable cible (target) :", target_stddev)
    mlflow.spark.log_model(model, "spark-model-lr")

  
  

#-------- Mise en place du Random Forest

with mlflow.start_run(run_name="Ecobalyse test Random Forest"):
    # Création de l'estimateur Random Forest Regression
    rf = RandomForestRegressor(featuresCol="features", labelCol="label")

    # Création du pipeline avec l'indexeur de caractéristiques
    pipeline_rf = Pipeline(stages=[featureIndexer, rf])

    # Entraînement du modèle
    model_rf = pipeline_rf.fit(train)

    # Faire des prédictions sur les données de test
    predictions_rf = model_rf.transform(test)

    # Évaluation du modèle en calculant le RMSE
    rmse_rf = evaluator.evaluate(predictions_rf)
    print("Root Mean Squared Error (RMSE) with Random Forest Regression:", rmse_rf)

    # Calcul de l'écart type de la variable cible dans les données de test
    target_stddev_rf = test.select(stddev("label")).collect()[0][0]
    print("Écart type de la variable cible (target) :", target_stddev_rf)
    mlflow.spark.log_model(model, "spark-model-rf")


#-------- Mise en place du Dummy Regressor

with mlflow.start_run(run_name="Ecobalyse test Dummy Regressor"):
    # Calculer la moyenne de la variable cible dans les données de test
    mean_target = train.selectExpr("avg(label)").collect()[0][0]
    # Créer un DataFrame avec une colonne de prédictions constantes basées sur la moyenne de la variable cible
    predictions_dummy = test.withColumn("prediction", lit(mean_target))

    # Calculer RMSE
    rmse_dummy = evaluator.evaluate(predictions_dummy)
    print("Root Mean Squared Error (RMSE) with DummyRegressor:", rmse_dummy)

    # Calculer l'écart type de la variable cible dans les données de test
    target_stddev = test.select(stddev("label")).collect()[0][0]
    print("Écart type de la variable cible (target) :", target_stddev)
    mlflow.spark.log_model(model, "spark-model-dr")

# Arrêter la session Spark

spark.stop()
