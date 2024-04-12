
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Create a new client and connect to the server
uri = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

# Load Ecobalyse database
ecobalyse = client["ecobalyse"]

# Define new indexes for each collection
indexes_to_create = [
    ("products", "id"),
    ("countries", "name"),
    ("fabricProcess", "id"),
    ("materials", "id"),
    ("impacts", "impacts"),
    ("impacts", "inputs"),
    ("impacts", "md5_id")
]

# Loop over collections and attributes to create indexes if necessary
for collection_name, field_name in indexes_to_create:
    collection = ecobalyse[collection_name]
    index_info = collection.index_information()
    index_name = f"{field_name}_1"  # Nom de l'index
    if index_name not in index_info:
        collection.create_index([(field_name, 1)])