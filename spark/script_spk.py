from pyspark.sql import SparkSession
import os
from mongo_module import Mongo
from pyspark.sql.functions import expr
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType
from pyspark.sql.functions import count
from pyspark.sql.functions import lit


# Create uri
uri = f"mongodb+srv://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0"

# Create Spark Session
spark = SparkSession.builder \
    .appName("MongoDB Spark Connector Example") \
    .getOrCreate()

# Load data collections into Spark DataFrames and store them into Spark dfs
collections = ["countries", "materials", "products", "fabricProcess", "products_details", "impacts", "impacts_documentation"]
dfs = {}

for collection in collections:
    df = spark.read.format("mongo").option("uri", uri).option("database", "ecobalyse").option("collection", collection).load()
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

# Write Spark datafrale into MongoDB
def write_spark_data_mongodb(data, collection_name):
    data.write \
        .format("mongo") \
        .option("database", "ecobalyse") \
        .option("collection", collection_name) \
        .mode("append") \
        .save()
    
#------------------------COUNTRIES STATS-------------------------

# Compute nb of occurences per country for countryFabric.name et countryMaking.name
fabric_countries_counts = dfs["impacts"].groupBy("product_id", "inputs.countryFabric.name") \
                               .agg(count("*").alias("countryFabric_count"))

making_countries_counts = dfs["impacts"].groupBy("product_id", "inputs.countryMaking.name") \
                               .agg(count("*").alias("countryMaking_count"))

# Merge fabric and making countries counts
merged_counts = fabric_countries_counts.join(making_countries_counts, 
                                   (fabric_countries_counts["product_id"] == making_countries_counts["product_id"]) &
                                   (fabric_countries_counts["name"] == making_countries_counts["name"]),
                                   "inner") \
                             .select(fabric_countries_counts["product_id"], 
                                     fabric_countries_counts["name"].alias("country_name"), 
                                     fabric_countries_counts["countryFabric_count"], 
                                     making_countries_counts["countryMaking_count"])

# Compute total number of products by type of product in database
total_count = dfs["impacts"].groupBy("product_id").count().alias("total_products")

# Join results
stats_countries = merged_counts.join(total_count, ["product_id"], "left")

#Write data into MongoDB Atlas
Mongo.create_collection("stats_countries")
write_spark_data_mongodb(stats_countries, 'stats_countries' )

#------------------------DAYS OF WEAR STATS-------------------------

# Compute statistics about days of wear metric by product category
stats_days_of_wear = dfs["impacts"].groupBy("product_id") \
    .agg(
        expr("percentile_approx(daysOfWear, 0.25)").alias("Q1"),
        expr("percentile_approx(daysOfWear, 0.5)").alias("mediane"),
        expr("percentile_approx(daysOfWear, 0.75)").alias("Q3"),
        expr("min(daysOfWear)").alias("min"),
        expr("max(daysOfWear)").alias("max"),
        expr("avg(daysOfWear)").alias("moyenne")
    )
Mongo.create_collection("stats_days_of_wear")
write_spark_data_mongodb(stats_days_of_wear, 'stats_days_of_wear' )

#------------------------IMPACT STATS-------------------------

# Impacts distribution per product category
sub_keys = dfs['impacts'].select('impacts.*').schema.names

stats_impacts = None
for sub_key in sub_keys:
    stats = dfs["impacts"].groupBy('product_id').agg(
        expr(f"percentile_approx(impacts.{sub_key}, 0.25) as Q1"),
        expr(f"percentile_approx(impacts.{sub_key}, 0.5) as median"),
        expr(f"percentile_approx(impacts.{sub_key}, 0.75) as Q3"),
        expr(f"mean(impacts.{sub_key}) as mean"),
        expr(f"min(impacts.{sub_key}) as min"),
        expr(f"max(impacts.{sub_key}) as max"),
        expr(f"Q1-1.5*(Q3-Q1) as seuil_min"),
        expr(f"Q3+1.5*(Q3-Q1) as seuil_max")
    ).withColumn("impact_type", lit(sub_key))
    if stats_impacts is None:
        stats_impacts = stats
    else:
        stats_impacts = stats_impacts.unionAll(stats)

Mongo.create_collection("stats_impacts")
write_spark_data_mongodb(stats_impacts, 'stats_impacts')

#------------------------OUTLIERS STATS-------------------------

# Identify product outliers based on impact level
product_types = dfs["impacts"].select("product_id").distinct().rdd.flatMap(lambda x: x).collect()

stats_outliers = None
for sub_key in sub_keys:
    for product_type in product_types:
        seuil_max = stats_impacts.filter((col("impact_type") == sub_key) & (col("product_id") == product_type)).select(f'seuil_max').rdd.flatMap(lambda x: x).collect()[0]
        seuil_min = stats_impacts.filter((col("impact_type") == sub_key) & (col("product_id") == product_type)).select(f'seuil_min').rdd.flatMap(lambda x: x).collect()[0]
        outliers = dfs["impacts"].filter((col("product_id") == product_type) & ((col(f"impacts.{sub_key}") >= seuil_max) | (col(f"impacts.{sub_key}") <= seuil_min))).select("md5_id","inputs.*").withColumn("impact_type", lit(sub_key))
    if stats_outliers is None:
        stats_outliers = outliers
    else:
        stats_outliers = stats_outliers.unionAll(outliers)

Mongo.create_collection("stats_outliers")
write_spark_data_mongodb(stats_outliers, 'stats_outliers')

#------------------------IMPACT RANKING STATS-------------------------
# top 5 products with highest global impact
highest_impact = dfs["impacts"].select("inputs.product.*") \
    .orderBy(col("impacts.ecs") , ascending=False) \
    .limit(10) \
    .withColumn("ranking", lit("highest_impact"))

# top 5 products with lowest global impact
lowest_impact = dfs["impacts"].select("inputs.product.*") \
    .orderBy(col("impacts.ecs") , ascending=True) \
    .limit(20) \
    .withColumn("ranking", lit("lowest_impact"))

stats_ranking = highest_impact.unionAll(lowest_impact)

Mongo.create_collection("stats_ranking")
write_spark_data_mongodb(stats_ranking, 'stats_ranking')


# Close Spark Session
spark.stop()