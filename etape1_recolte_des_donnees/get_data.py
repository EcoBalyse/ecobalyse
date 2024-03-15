#!/usr/bin/env python3
"""
Created on Wed Mar 06 21:28:47 2024.

"""

# %%
import requests
import sys
import argparse
import json
import pandas as pd
from random import randint

# %%

def readfile(path):
    """ read file """
    if path != None or path != "":
        return [line.strip() for line in open(path, 'r')]
    return

def ragent():
    """random agent"""
    user_agents = ()
    realpath = "useragent"
    for _ in readfile(realpath):
        user_agents += (_,)
    return user_agents[randint(0, len(user_agents)-1)]

def main():
    verbose = False

    # Declare Available arguments
    parser = argparse.ArgumentParser(
        description='EcoBalyse : get_data')
    parser.add_argument("-t", "--type", help="Textile type")
    parser.add_argument("-v", "--verbose", help="Print informations", action="store_true")

    args = parser.parse_args()

    # Parse arguments
    if args.verbose:
        verbose = True
    if args.type:
        arg_textile_type = args.type
    else:
        print("Textile type is needed !")
        exit()

    headers = {
        'User-Agent': ragent(),
        'accept': 'application/json',
    }

    df_countries = pd.read_json('json/countries.json')

    # Charger le fichier JSON
    with open('json/products_details.json') as f:
        data = json.load(f)

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
    }

    concatenated_df = pd.DataFrame()

    for textile_type, exemples in data.items():
        if textile_type == arg_textile_type:
            if verbose:
                print(f"Type : {textile_type}")

            for exemple in exemples:
                mass_min, mass_max, increment = exemple['mass']
                mass = mass_min
                while mass < mass_max:
                    mass = round(mass, 2)
                    if verbose:
                        print(f"Mass : {mass}")

                    # df_countries.iloc[[4, 10]]["code"]

                    for fabric_country in df_countries["code"]:
                        for material_country in df_countries["code"]:
                            tab_materials = []
                            for material, percentage in exemple['materials'].items():
                                tab_materials.append({"id": material, "share": percentage/100, "country": material_country})

                            if verbose:
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

            break

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        sys.stdout.write('[+] Exit requested')