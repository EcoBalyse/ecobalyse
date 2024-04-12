from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0"

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

def get_avg_product_list_mongo(product_id: str, sort: int, nb_doc: int):
    pipeline = [
        {
            "$match": {"inputs.product.id": product_id}  # Filtrer par inputs.product.id
        },
        {
            "$project": {
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

    results = [doc for doc in result_cursor]

    return results

def get_product_list_country_mongo(product_id: str, country: str, nb_doc: int):
    result_cursor = ecobalyse['impacts'].find({"inputs.product.id": product_id, "inputs.countryFabric.code": country}, {'_id': 0}).limit(nb_doc)

    results = [doc for doc in result_cursor]

    return results

def search_product_md5_id_mongo(md5_id: str):
    return ecobalyse['impacts'].count_documents({"md5_id": md5_id})

def insert_product_mongo(product):
    try:
        result = ecobalyse["impacts"].insert_one(product)

        return True
    except:
        return False

def delete_product_mongo(md5_id: str):
    return ecobalyse["impacts"].delete_one({"md5_id": md5_id})