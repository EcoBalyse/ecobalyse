
from pymongo import MongoClient
from pprint import pprint
import json

client = MongoClient(
    host="127.0.0.1",
    port = 27017
)

# Create Ecobalyse database
ecobalyse = client["ecobalyse"]
print(client.list_database_names())

# Create collections
collections = ["countries", "materials", "products", "fabricProcess", "products_details"]

for collection_name in collections:
    if collection_name not in ecobalyse.list_collection_names():
        ecobalyse.create_collection(collection_name)
        print(f"La collection {collection_name} a été créée.")

# Load JSON files and insert data into collections
for collection_name in collections:
    with open(f'json/{collection_name}.json', 'r') as file:
        data = json.load(file)
        if collection_name == "products_details":
            data = [data]
        ecobalyse[collection_name].insert_many(data, ordered = False)
        print(f"Données insérées dans la collection {collection_name}.")
