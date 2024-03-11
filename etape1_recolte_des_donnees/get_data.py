#!/usr/bin/env python3
"""
Created on Wed Mar 06 21:28:47 2024.

"""

# %%
import requests
import pandas as pd
import ast
import os
import json

import sqlite3

con = sqlite3.connect("test.db")

# %%

headers = {
    'accept': 'application/json',
}

response = requests.get('https://ecobalyse.beta.gouv.fr/api/textile/countries', headers=headers, timeout=10)
lst_countries = ast.literal_eval(response.text)
df_countries = pd.DataFrame(lst_countries)
df_countries.to_csv("countries.csv", index=False)

response = requests.get('https://ecobalyse.beta.gouv.fr/api/textile/materials', headers=headers, timeout=10)
lst_materials = ast.literal_eval(response.text)
df_materials = pd.DataFrame(lst_materials)
df_materials.to_csv("materials.csv", index=False)

# response = requests.get('https://ecobalyse.beta.gouv.fr/api/textile/products', headers=headers, timeout=10)
# lst_products = ast.literal_eval(response.text)
# df_products = pd.DataFrame(lst_products)
# df_products.to_csv("products.csv", index=False)

# Charger le fichier JSON
with open('products_details.json') as f:
    data = json.load(f)

headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
}

df = pd.DataFrame()

for textile_type, exemples in data.items():
    print(f"Type : {textile_type}")

    for exemple in exemples:
        mass_min, mass_max = exemple['mass']
        mass = mass_min
        while mass < mass_max:
            mass = round(mass, 2)
            print(f"Mass : {mass}")

            for spinning_country in df_countries.iloc[[4, 10]]["code"]:
                for fabric_country in df_countries.iloc[[4, 10]]["code"]:
                    for dyeing_country in df_countries.iloc[[4, 10]]["code"]:
                        for making_country in df_countries.iloc[[4, 10]]["code"]:
                            for material_country in df_countries.iloc[[4, 10]]["code"]:
                                tab_materials = []
                                for material, percentage in exemple['materials'].items():
                                    tab_materials.append({"id": material, "share": percentage/100, "country": material_country})

                                print(f"Materials : {tab_materials}")

                                json_data = {
                                    'mass': mass,
                                    'materials': tab_materials,
                                    'product': textile_type,
                                    'countrySpinning': spinning_country,
                                    'countryFabric': fabric_country,
                                    'countryDyeing': dyeing_country,
                                    'countryMaking': making_country,
                                    'fabricProcess': exemple['fabricProcess'],
                                }

                                response = requests.post('https://ecobalyse.beta.gouv.fr/api/textile/simulator', headers=headers, json=json_data)

                                rep = ast.literal_eval(response.text)
                                rep.update({f"impact_{key}": value for key, value in rep["impacts"].items()})
                                _ = rep.pop("impacts")
                                rep.update(rep["query"])
                                _ = rep.pop("query")
                                rep.update({f"{elt['id']}_{elt['country']}": elt["share"] for elt in rep["materials"]})
                                _ = rep.pop("materials")

                                df_tmp = pd.DataFrame(rep, index=[0])

                                df = pd.concat([df, df_tmp])
                    
            mass += 0.01  # Augmente le poids par pas de 0.01 kg

df.to_csv("test.csv", index=False)

# %%
df.to_sql("impacts", con, if_exists="append")

# %%

cur = con.cursor()
pd.DataFrame(cur.execute("SELECT * FROM impacts").fetchall())

# %%

json_data = {
    'mass': 0.3,
    'materials': [
        {
            'id': 'coton',
            'share': 1,
            'country': "IT",
        },
    ],
    'product': "tshirt",
    'countrySpinning': 'FR',
    'countryFabric': 'FR',
    'countryDyeing': 'FR',
    'countryMaking': "FR",
    'fabricProcess': 'knitting-mix',
}

response = requests.post('https://ecobalyse.beta.gouv.fr/api/textile/simulator', headers=headers, json=json_data)

rep = ast.literal_eval(response.text)
rep.update({f"impact_{key}": value for key, value in rep["impacts"].items()})
_ = rep.pop("impacts")
rep.update(rep["query"])
_ = rep.pop("query")
rep.update({f"{elt['id']}_{elt['country']}": elt["share"] for elt in rep["materials"]})
_ = rep.pop("materials")

df_tmp = pd.DataFrame(rep, index=[0])

# %%
target_name = "impacts"
target_cols = pd.read_sql_query(f"select * from {target_name} limit 1;", con).columns.tolist()
your_cols = df_tmp.columns.tolist()

if set(your_cols) - set(target_cols) == set():
    print("Les colonnes matchs")
else:
    lst_cols = list(set(your_cols) - set(target_cols))
    print("Les colonnes ne matchent pas")
    print(lst_cols)
    for col in lst_cols:
        cur.execute(f"ALTER TABLE impacts ADD {col} VARCHAR;")

df_tmp.to_sql("impacts", con, if_exists="append")

# %%

df_tmp.to_sql("impacts", con, if_exists="append")

# %%

cur = con.cursor()
pd.DataFrame(cur.execute("SELECT * FROM impacts").fetchall())
