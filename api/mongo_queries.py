from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os

# Connect to MongoDB using environment variables
mongo_uri = f"mongodb+srv://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
ecobalyse = client["ecobalyse"]

# Function to get product ID list
def get_product_id_mongo():
    """
    Get product ID list from 'impacts' collection
    """
    return ecobalyse['impacts'].distinct("inputs.product.id")

# Function to get product list by ID
def get_product_list_mongo(product_id: str, nb_doc: int):
    """
    Get product list by ID from 'impacts' collection
    """
    result_cursor = ecobalyse['impacts'].find({"inputs.product.id": product_id}, {'_id': 0}).limit(nb_doc)

    results = [doc for doc in result_cursor]

    return results

# Function to get average product list by ID
def get_avg_product_list_mongo(product_id: str, sort: int, nb_doc: int):
    """
    Get average product list by ID from 'impacts' collection
    """
    pipeline = [
        {
            "$match": {"inputs.product.id": product_id}  # Filtrer par inputs.product.id
        },
        {
            "$project": {
                "inputs": "$inputs",
                "average_impacts": {
                    "$avg": [
                        "$impacts.acd", "$impacts.cch", "$impacts.etf", "$impacts.etf-c",
                        "$impacts.fru", "$impacts.fwe", "$impacts.htc", "$impacts.htc-c",
                        "$impacts.htn", "$impacts.htn-c", "$impacts.ior", "$impacts.ldu",
                        "$impacts.mru", "$impacts.ozd", "$impacts.pco", "$impacts.pma",
                        "$impacts.swe", "$impacts.tre", "$impacts.wtu", "$impacts.ecs",
                        "$impacts.pef"
                    ]
                }
            }
        },
        {
            "$sort": {"average_impacts": sort}  # Tri par ordre décroissant de la moyenne des impacts
        },
        {
            "$limit": nb_doc  # Limite du nombre de résultats à retourner
        }
    ]

    result_cursor = list(ecobalyse['impacts'].aggregate(pipeline))

    for doc in result_cursor:
        del doc["_id"]

    results = [doc for doc in result_cursor]

    return results

# Function to get product list by ID and country
def get_product_list_country_mongo(product_id: str, country: str, nb_doc: int):
    """
    Get product list by ID and country from 'impacts' collection
    """
    result_cursor = ecobalyse['impacts'].find({"inputs.product.id": product_id, "inputs.countryFabric.code": country}, {'_id': 0}).limit(nb_doc)

    results = [doc for doc in result_cursor]

    return results

# Function to search product by MD5 ID
def search_product_md5_id_mongo(md5_id: str):
    """
    Search product by MD5 ID in 'impacts' collection
    """
    return ecobalyse['impacts'].count_documents({"md5_id": md5_id})

# Function to insert new product
def insert_product_mongo(product):
    """
    Insert new product into 'impacts' collection
    """
    try:
        result = ecobalyse["impacts"].insert_one(product)

        return True
    except:
        return False

# Function to delete product by MD5 ID
def delete_product_mongo(md5_id: str):
    """
    Delete product by MD5 ID from 'impacts' collection
    """
    return ecobalyse["impacts"].delete_one({"md5_id": md5_id})

# Functions to get statistics
def get_stats_countries_mongo():
    """
    Get country statistics from 'stats_countries' collection
    """
    result_cursor = ecobalyse['stats_countries'].find({}, {'_id': 0})

    results = [doc for doc in result_cursor]

    return results

def get_stats_days_of_wear_mongo():
    """
    Get days of wear statistics from 'stats_days_of_wear' collection
    """
    result_cursor = ecobalyse['stats_days_of_wear'].find({}, {'_id': 0})

    results = [doc for doc in result_cursor]

    return results

def get_stats_impacts_mongo():
    """
    Get impact statistics from 'stats_impacts' collection
    """
    result_cursor = ecobalyse['stats_impacts'].find({}, {'_id': 0})

    results = [doc for doc in result_cursor]

    return results

def get_stats_outliers_mongo():
    """
    Get outlier statistics from 'stats_outliers' collection
    """
    result_cursor = ecobalyse['stats_outliers'].find({}, {'_id': 0}).limit(200)

    results = [doc for doc in result_cursor]

    return results

def get_stats_ranking_mongo():
    """
    Get product ranking statistics from 'stats_ranking' collection
    """
    result_cursor = ecobalyse['stats_ranking'].find({}, {'_id': 0})

    results = [doc for doc in result_cursor]

    return results
