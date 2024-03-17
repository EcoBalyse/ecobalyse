#!/usr/bin/env python3
"""
Created on Wed Mar 06 21:28:47 2024.

"""

# %%
import requests
import json

headers = {
    'accept': 'application/json',
}

### COUNTRIES ###
response = requests.get('https://ecobalyse.beta.gouv.fr/api/textile/countries', headers=headers, timeout=10)

if response.status_code == 200:
    json_data = response.json()

    with open('json/countries.json', 'w') as json_file:
        json.dump(json_data, json_file)

### MATERIALS ###
response = requests.get('https://ecobalyse.beta.gouv.fr/api/textile/materials', headers=headers, timeout=10)

if response.status_code == 200:
    json_data = response.json()

    with open('json/materials.json', 'w') as json_file:
        json.dump(json_data, json_file)