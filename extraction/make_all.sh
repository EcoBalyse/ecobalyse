#!/bin/bash
#
#
#

### Make JSON ###
python3 get_json.py

### Make extraction ###
python3 get_data.py -t all -v

### Create Database MongoDB Atlas ###
#python3 create_mongodb.py

### Create Database Index ###
#python3 create_indexes.py

### Create Database Documentation ###
#python3 create_doc_collection.py