
from pymongo import MongoClient
import json
import os

client = MongoClient(
    host="127.0.0.1",
    port = 27017,
    username = "admin",
    password = "pass"
)


# Create Ecobalyse database
ecobalyse = client["ecobalyse"]
print(client.list_database_names())

# Load impact files from 'data' folder
data = 'data/'
requests_json = []
for file in os.listdir(data):
    if file.endswith('.json'):
        file_path = os.path.join(data, file)
        with open(file_path, 'r') as file:
            data = json.load(file)
            requests_json.append(data)

collections = ["countries", "materials", "products", "fabricProcess", "products_details", "impacts"]

for collection_name in collections:
    
    # Create collections
    if collection_name not in ecobalyse.list_collection_names():
        ecobalyse.create_collection(collection_name)
        print(f"La collection {collection_name} a été créée.")
    else:
        ecobalyse[collection_name].delete_many({})  

    # Load input files from 'json' folder
    if collection_name != "impacts":
        with open(f'json/{collection_name}.json', 'r') as file:
            data = json.load(file)
            if collection_name == "products_details":
                data = [data]
    # Add product_id parameter to all impact documents
    else :
        for data in requests_json:
            for documents in data:                
                product_id = documents.get("inputs", {}).get("product", {}).get("id")        
                documents["product_id"] = product_id
    # Insert inputs and impact data into created collections
    ecobalyse[collection_name].insert_many(data, ordered = False)
    print(f"Données insérées dans la collection {collection_name}.")
