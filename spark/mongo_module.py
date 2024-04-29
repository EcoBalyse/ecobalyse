from pymongo import MongoClient
import os

class Mongo:
    def __init__(self):
        """
        Initialize the MongoDB connection and database.
        """
        self.uri = f"mongodb+srv://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0"
        self.db_name = 'ecobalyse'  
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]

    @staticmethod
    def create_collection(collection_name):
        """
        Create a new collection in the database.
        :param collection_name: The name of the collection to create.
        """
        mongo_instance = Mongo()
        db = mongo_instance.db
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"The collection {collection_name} was created in the database {mongo_instance.db_name}.")
        else:
            db[collection_name].delete_many({})  

    @staticmethod
    def insert_data_into_collection(collection_name, data):
        """
        Insert data into a collection in the database.
        :param collection_name: The name of the collection to insert data into.
        :param data: The data to insert.
        """
        mongo_instance = Mongo()
        db = mongo_instance.db
        collection = db[collection_name]
        if isinstance(data, list):
            result = collection.insert_many(data)
            print(f"{len(result.inserted_ids)} documents inserted into '{collection_name}' collection")
        elif isinstance(data, dict):
            result = collection.insert_one(data)
            print(f"Document inserted into '{collection_name}' collection with _id: {result.inserted_id}")
        else:
            raise ValueError("Data must be a dictionary or a list of dictionaries")
