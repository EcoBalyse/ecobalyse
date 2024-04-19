#!/bin/bash
#
#
#

### Make JSON ###
python3 /extraction/get_json.py

### Make extraction ###
python3 /extraction/get_data.py -t all -v

### Create Database MongoDB Atlas ###
python3 /extraction/create_mongodb.py

### Create Database Documentation ###
python3 /extraction/create_doc_collection.py