
from pymongo import MongoClient
from pprint import pprint
import json
from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# client = MongoClient(
#     host="127.0.0.1",
#     port = 27017,
#     username = "admin",
#     password = "pass"
# )

uri = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri)


# Create Ecobalyse databasedocke
ecobalyse = client["ecobalyse"]
print(client.list_database_names())

print(ecobalyse.list_collection_names())
pprint(ecobalyse["impacts"].distinct("product_id"))

# Retrieve collections list in database
collections = ecobalyse.list_collection_names()

# For each collection, print indexes
for collection_name in collections:
    collection = ecobalyse[collection_name]
    indexes = collection.list_indexes()
    
    print(f"Indexes for collection '{collection_name}':")
    for index in indexes:
        print(index)

# Fermer la connexion
client.close()