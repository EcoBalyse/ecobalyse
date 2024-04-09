from dotenv import load_dotenv
from pyspark.sql import SparkSession
import os
from pyspark.sql.functions import expr
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType

load_dotenv()

# Create uri
uri = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@cluster0.mudexs5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

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

# Define database and collections
database = "ecobalyse"
collections = ["countries", "materials", "products", "fabricProcess", "products_details", "impacts", "impacts_documentation"]

# Dictionnary to store collections
dfs = {}

# Load data collections into Spark DataFrames and store them into Spark dfs
for collection in collections:
    df = spark.read.format("mongo").option("collection", collection).load()
    dfs[collection] = df

# Select distinct countries
dfs["impacts"].select("countryFabric.name").distinct()
dfs["impacts"].select("countryMaking.name").distinct()

# Compute statistics about days of wear metric by product category
daysofwear_by_category = dfs["impacts"].groupBy("product_id") \
    .agg(
        expr("percentile_approx(daysOfWear, 0.25)").alias("Q1"),
        expr("percentile_approx(daysOfWear, 0.5)").alias("mediane"),
        expr("percentile_approx(daysOfWear, 0.75)").alias("Q3"),
        expr("min(daysOfWear)").alias("min"),
        expr("max(daysOfWear)").alias("max"),
        expr("avg(daysOfWear)").alias("moyenne")
    )
daysofwear_by_category.show()

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

# Impacts distribution per product category
sub_keys = ['acd', 'cch', 'etf', 'etf_c', 'fru', 'fwe', 'htc', 'htc_c', 'htn', 'htn_c', 'ior', 'ldu', 'mru', 'ozd', 'pco', 'pma', 'swe', 'tre', 'wtu', 'ecs', 'pef']
impacts_stats = {}
for sub_key in sub_keys:
    stats = dfs["impacts"].groupBy('product_id').agg(
        expr(f"percentile_approx(impacts.{sub_key}, 0.25) as Q1_{sub_key}"),
        expr(f"percentile_approx(impacts.{sub_key}, 0.5) as median_{sub_key}"),
        expr(f"percentile_approx(impacts.{sub_key}, 0.75) as Q3_{sub_key}"),
        expr(f"mean(impacts.{sub_key}) as mean_{sub_key}"),
        expr(f"min(impacts.{sub_key}) as min_{sub_key}"),
        expr(f"max(impacts.{sub_key}) as max_{sub_key}"),
        expr(f"Q1_{sub_key}-1.5*(Q3_{sub_key}-Q1_{sub_key}) as seuil_min_{sub_key}"),
        expr(f"Q3_{sub_key}+1.5*(Q3_{sub_key}-Q1_{sub_key}) as seuil_max_{sub_key}")
    )
    impacts_stats[sub_key] = stats
    
# Identify product outliers based on impact level
product_types = dfs["impacts"].select("product_id").distinct().rdd.flatMap(lambda x: x).collect()

outliers = {}
for sub_key in sub_keys:
    for product_type in product_types:
        seuil_max = impacts_stats[sub_key].filter(col("product_id")== product_type).select(f'seuil_max_{sub_key}').rdd.flatMap(lambda x: x).collect()[0]
        seuil_min = impacts_stats[sub_key].filter(col("product_id")== product_type).select(f'seuil_max_{sub_key}').rdd.flatMap(lambda x: x).collect()[0]
        outliers[f"{sub_key}_{product_type}"] = dfs["impacts"].filter((col("product_id")== product_type) & ((col(f"impacts.{sub_key}") >= seuil_max) | (col(f"impacts.{sub_key}") <= seuil_min))).select("inputs")
        

# top 5 products with biggest global impact
print("Cinq produits avec le plus grand impact global :")
dfs["impacts"].select("inputs.product") \
    .orderBy(col("impacts.ecs") , ascending=False) \
    .limit(5) \
    .show(truncate=False)

# top 5 products with lowest global impact
print("Cinq produits avec le plus grand impact global :")
dfs["impacts"].select("inputs.product") \
    .orderBy(col("impacts.ecs") , ascending=True) \
    .limit(5) \
    .show(truncate=False)
 
# Fermer la session Spark
spark.stop()