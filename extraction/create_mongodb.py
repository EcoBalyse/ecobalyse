
from pymongo import MongoClient
import json
import os
import hashlib
import argparse
import sys

def main():
    reset = False

    # Declare Available arguments
    parser = argparse.ArgumentParser(
        description='EcoBalyse : Create MongoDB Atlas')
    parser.add_argument("-i", "--init", help="Reset Database", action="store_true")

    args = parser.parse_args()

    # Parse arguments
    if args.init:
        reset = True

    uri = f"mongodb+srv://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0"
    # Create a new client and connect to the server
    client = MongoClient(uri)


    # Create Ecobalyse database
    ecobalyse = client["ecobalyse"]
    print(client.list_database_names())

    # Load impact files from 'data' folder
    data_folder = '/data/'
    requests_json = []
    if os.path.exists(data_folder) and os.path.isdir(data_folder):
        for file_name in os.listdir(data_folder):
            if file_name.endswith('.json'):
                file_path = os.path.join(data_folder, file_name)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    requests_json.append(data)

    collections = ["countries", "materials", "products", "fabricProcess", "products_details", "impacts"]

    # Define new indexes for each collection
    indexes_to_create = [
        ("products", "id"),
        ("countries", "code"),
        ("countries", "name"),
        ("fabricProcess", "id"),
        ("materials", "id"),
        ("impacts", "impacts"),
        ("impacts", "inputs"),
        ("impacts", "product_id"),
        ("impacts", "md5_id")
    ]

    for collection_name in collections:
        # Create collections
        if collection_name not in ecobalyse.list_collection_names():
            ecobalyse.create_collection(collection_name)
            print(f"La collection {collection_name} a été créée.")

            if collection_name == "impacts":
                reset = True
        else:
            if collection_name != "impacts" or reset:
                ecobalyse[collection_name].delete_many({})

        # Create index
        matching_indexes = filter(lambda x: x[0] == collection_name, indexes_to_create)

        for index_collection_name, field_name in matching_indexes:
            collection = ecobalyse[collection_name]
            index_info = collection.index_information()
            index_name = f"{field_name}_1"  # Nom de l'index
            if index_name not in index_info:
                collection.create_index([(field_name, 1)])

        # Load input files from 'json' folder
        if collection_name != "impacts":
            if collection_name == "products_details":
                json_file = f'/products/{collection_name}.json'
            else:
                json_file = f'/json/{collection_name}.json'

            if os.path.exists(json_file):
                with open(json_file, 'r') as file:
                    data = json.load(file)
                    if collection_name == "products_details":
                        data = [data]
                # Insert input data into created collections
                ecobalyse[collection_name].insert_many(data, ordered = False)

        # Add product_id parameter at the first level of dictionnary ofr impact data
        elif len(requests_json) > 0 :
            for json_data in requests_json:
                for documents in json_data:                
                    product_id = documents.get("inputs", {}).get("product", {}).get("id")        
                    documents["product_id"] = product_id

                    if not reset:
                        # Find product by md5_id
                        data = ecobalyse[collection_name].find_one({'md5_id': documents['md5_id']})

                        if data is not None:
                            del data['_id']

                            # "md5_check" for documents
                            json_str = json.dumps(documents, sort_keys=True)
                            md5_check_documents = hashlib.md5(json_str.encode()).hexdigest()

                            # "md5_check" poforur data
                            json_str = json.dumps(data, sort_keys=True)
                            md5_check_data = hashlib.md5(json_str.encode()).hexdigest()

                            # Modifications ?
                            if md5_check_documents != md5_check_data:
                                ecobalyse[collection_name].update_one({'md5_id': documents['md5_id']}, {'$set': documents})
                        else:
                            ecobalyse[collection_name].insert_one(documents)

                if reset:
                    # Insert impact data into created collections
                    ecobalyse[collection_name].insert_many(json_data, ordered = False)
        
            print(f"Données insérées dans la collection {collection_name}.")

    # Fermer la connexion
    client.close()

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        sys.stdout.write('[+] Exit requested')