#!/usr/bin/env python3
"""
Created on Wed Mar 06 21:28:47 2024.

This script fetches data from the EcoBalyse API and saves it to JSON files.

"""

# %%
import requests
import json

# Set the headers for the API request
headers = {
    'accept': 'application/json',
}

### COUNTRIES ###
# Send a GET request to the EcoBalyse API to fetch data on countries
response = requests.get('https://ecobalyse.beta.gouv.fr/api/textile/countries', headers=headers, timeout=10)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response as JSON data
    json_data = response.json()

    # Save the JSON data to a file
    with open('/json/countries.json', 'w') as json_file:
        json.dump(json_data, json_file)
else:
    print("Error ecobalyse.beta.gouv.fr status_code:", response.status_code)

### MATERIALS ###
# Send a GET request to the EcoBalyse API to fetch data on materials
response = requests.get('https://ecobalyse.beta.gouv.fr/api/textile/materials', headers=headers, timeout=10)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response as JSON data
    json_data = response.json()

    # Save the JSON data to a file
    with open('/json/materials.json', 'w') as json_file:
        json.dump(json_data, json_file)
else:
    print("Error ecobalyse.beta.gouv.fr status_code:", response.status_code)