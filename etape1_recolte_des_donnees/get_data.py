#!/usr/bin/env python3
"""
Created on Wed Mar 06 21:28:47 2024.

"""

# %%
import requests
import os
import json
import pandas as pd

# %%

headers = {
    'accept': 'application/json',
}

df_countries = pd.read_json('json/countries.json')
df_materials = pd.read_json("json/materials.json")

# Charger le fichier JSON
with open('json/products_details.json') as f:
    data = json.load(f)

headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
}

concatenated_df = pd.DataFrame()

for textile_type, exemples in data.items():
    print(f"Type : {textile_type}")

    for exemple in exemples:
        mass_min, mass_max, increment = exemple['mass']
        mass = mass_min
        while mass < mass_max:
            mass = round(mass, 2)
            print(f"Mass : {mass}")

            # df_countries.iloc[[4, 10]]["code"]

            for fabric_country in df_countries["code"]:
                for material_country in df_countries["code"]:
                    tab_materials = []
                    for material, percentage in exemple['materials'].items():
                        tab_materials.append({"id": material, "share": percentage/100, "country": material_country})

                    print(f"Materials : {tab_materials}")

                    json_data = {
                        'mass': mass,
                        'materials': tab_materials,
                        'product': textile_type,
                        'countrySpinning': fabric_country,
                        'countryFabric': fabric_country,
                        'countryDyeing': fabric_country,
                        'countryMaking': fabric_country,
                        'fabricProcess': exemple['fabricProcess'],
                    }

                    response = requests.post('https://ecobalyse.beta.gouv.fr/api/textile/simulator/detailed', headers=headers, json=json_data)

                    if response.status_code == 200:
                        df = pd.DataFrame([response.json()])

                        concatenated_df = pd.concat([concatenated_df, df], ignore_index=True)
                    
            mass += increment  # Augmente le poids par pas

    concatenated_df.reset_index(drop=True, inplace=True)

    # Enregistrement du DataFrame fusionné dans un fichier JSON
    output_file = f"data/{textile_type}.json"
    concatenated_df.to_json(output_file, orient="records", indent=4)

    concatenated_df = pd.DataFrame()