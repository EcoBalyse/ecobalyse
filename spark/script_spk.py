from dotenv import load_dotenv
from pyspark.sql import SparkSession
import os

load_dotenv()

#os.environ["SPARK_HOME"] = "/opt/spark/spark-3.2.4"

# Create uri
uri = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@cluster0.mudexs5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create Spark
spark = SparkSession.builder \
    .appName("MongoDB Spark Connector Example") \
    .config("spark.mongodb.input.uri", uri) \
    .config("spark.mongodb.output.uri", uri) \
    .config("spark.mongodb.input.database", "ecobalyse") \
    .config("spark.mongodb.input.collection", "impacts") \
    .config("spark.mongodb.output.database", "ecobalyse") \
    .config("spark.mongodb.output.collection", "impacts") \
    .getOrCreate()

df = spark.read.format("mongo").load()

df.show()
exit()

# Define database and collections
database = "ecobalyse"
collections = ["countries", "materials", "products", "fabricProcess", "products_details", "impacts"]

# Dictionnary to store collections
dfs = {}

# Load data collections into Spark DataFrames and store them into dfs
for collection in collections:
    df = spark.read.format("mongodb").option("uri", uri).option("collection", collection).option("database", "ecobalyse").load()
    dfs[collection] = df

# Print schemas and first rows for each DataFrame
for collection, df in dfs.items():
    print(f"Affichage des données de la collection '{collection}' :")
    df.printSchema()
    df.show()

spark.stop()