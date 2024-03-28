
from pymongo import MongoClient
from pprint import pprint
import json
from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Create a new client and connect to the server
uri = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@cluster0.mudexs5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

# Load Ecobalyse database
ecobalyse = client["ecobalyse"]

# Retrieve collections list in database
collections = ecobalyse.list_collection_names()

# For each collection, print indexes
for collection_name in collections:
    collection = ecobalyse[collection_name]
    indexes = collection.list_indexes()
    
    print(f"Indexes for collection '{collection_name}':")
    for index in indexes:
        print(index)
    print()
