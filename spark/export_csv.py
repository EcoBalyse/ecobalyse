import csv
from pymongo import MongoClient

# Connect to MongoDB Atlas
client = MongoClient(f"mongodb+srv://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_CLUSTER')}/?retryWrites=true&w=majority&appName=Cluster0")
db = client["ecobalyse"]
collection = db["impacts"]

# Define the fields to export
fields = ["ecs", "product_id", "MaterialId_1", "MaterialId_2", "MaterialId_1_share", "MaterialId_2_share", "countryDyeingCode", "countryFabricCode", "countryMakingCode", "fabricProcess", "mass", "airTransportRatio"]

# Write the data to a CSV file
with open("ecobalyse_data.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    for document in collection.find():
        row = []
        for field in fields:
            if field in document:
                value = document[field]
            elif field in document["inputs"]:
                value = document["inputs"][field]
            elif field.startswith("MaterialId_") and field.endswith("_share"):
                material_number = int(field.split("_")[1])
                try:    
                    value = document["inputs"]["materials"][material_number - 1]["share"]
                except:
                    value = ''
            elif field.startswith("MaterialId_"):
                material_number = int(field.split("_")[1])
                try:
                    material = document["inputs"]["materials"][material_number - 1]["material"]
                    value = material["id"]
                except:
                    value = ''
            elif field.endswith("Code"):
                country_type = field.split("Code")[0]
                value = document["inputs"][country_type]["code"]
            elif field == "ecs":
                value = document["impacts"]["ecs"]
            else:
                value = document["inputs"].get(field, None)
            row.append(value)
        writer.writerow(row)