
from pymongo import MongoClient
from pprint import pprint
import json

client = MongoClient(
    host="127.0.0.1",
    port = 27017,
    username = "admin",
    password = "pass"
)


# Create Ecobalyse databasedocke
ecobalyse = client["ecobalyse"]
print(client.list_database_names())

print(ecobalyse.list_collection_names())
print(ecobalyse["countries"].find_one())
print(ecobalyse["products_details"].find_one())

