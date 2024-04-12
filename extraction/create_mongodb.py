
from pymongo import MongoClient
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


# Create Ecobalyse database
ecobalyse = client["ecobalyse"]
print(client.list_database_names())

# Load impact files from 'data' folder
data_folder = 'data/'
requests_json = []
for file_name in os.listdir(data_folder):
    if file_name.endswith('.json'):
        file_path = os.path.join(data_folder, file_name)
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
    # Insert input data into created collections
        ecobalyse[collection_name].insert_many(data, ordered = False)

    # Add product_id parameter at the first level of dictionnary ofr impact data
    else :
        for json_data in requests_json:
            for documents in json_data:                
                product_id = documents.get("inputs", {}).get("product", {}).get("id")        
                documents["product_id"] = product_id
    # Insert impact data into created collections
            ecobalyse[collection_name].insert_many(json_data, ordered = False)
    print(f"Données insérées dans la collection {collection_name}.")

# Fermer la connexion
client.close()