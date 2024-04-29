
from pymongo import MongoClient
import os
import requests

# Connection to MongoDB Atlas
uri = f"mongodb+srv://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
ecobalyse = client["ecobalyse"]

# Retrieval of JSON data from the documentation API
doc_collection = "impacts_documentation"
api_url = "https://ecobalyse.beta.gouv.fr/api"
response = requests.get(api_url)
data_json = response.json()

# Creation of a new collection
if doc_collection not in ecobalyse.list_collection_names():
    ecobalyse.create_collection(doc_collection)
    print(f"The collection {doc_collection} has been created.")
else:
    ecobalyse[doc_collection].delete_many({})  # Delete all documents in the collection

# Adding impact documentation to the collection
documentation = data_json.get('components', {}).get('schemas', {}).get('Impacts', {}).get('properties', {})
final_impacts_doc = []
for impact_code, details in documentation.items():
    if 'description' not in details:
        continue
    description = details.get('description')
    impact = {'code': impact_code, 'description': description}
    final_impacts_doc.append(impact)

ecobalyse[doc_collection].insert_many(final_impacts_doc, ordered = False)
print(f"Data inserted into the collection {doc_collection}.")

