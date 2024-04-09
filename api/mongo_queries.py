from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@cluster0.mudexs5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(mongo_uri)

# Ecobalyse database
ecobalyse = client["ecobalyse"]

def get_product_id_mongo():
    return ecobalyse['impacts'].distinct("inputs.product.id")

def get_product_list_mongo(product_id: str, nb_doc: int):
    result_cursor = ecobalyse['impacts'].find({"inputs.product.id": product_id}, {'_id': 0}).limit(nb_doc)

    results = [doc for doc in result_cursor]

    return results

def get_product_list_country_mongo(product_id: str, country: str, nb_doc: int):
    result_cursor = ecobalyse['impacts'].find({"inputs.product.id": product_id, "inputs.countryFabric.code": country}, {'_id': 0}).limit(nb_doc)

    results = [doc for doc in result_cursor]

    return results