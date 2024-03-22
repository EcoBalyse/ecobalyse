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
    parser.add_argument("-l", "--limit", help="Textile type limit")
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
    if args.limit:
        limit = int(args.limit)
    else:
        limit = 8000

    df_countries = pd.read_json('json/countries.json')

    # Charger le fichier JSON
    with open('json/products_details.json') as f:
        data = json.load(f)

    concatenated_df = pd.DataFrame()

    count = 0
    count_file = 1

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

                    for countrySpinning in df_countries["code"]:
                        for countryFabric in df_countries["code"]:
                            for countryDyeing in df_countries["code"]:
                                for countryMaking in df_countries["code"]:
                                    qualities = [0, 0.67, 1.45]
                                    reparabilities = [0, 1, 1.15]
                                    
                                    # Changed quality and reparability product
                                    for quality, reparability in zip(qualities, reparabilities):
                                        tab_materials = []
                                        for material, percentage in exemple['materials'].items():
                                            tab_materials.append({"id": material, "share": percentage/100})

                                        if verbose:
                                            print(f"Materials : {tab_materials}")

                                        json_data = {
                                            'mass': mass,
                                            'materials': tab_materials,
                                            'product': textile_type,
                                            'countrySpinning': countrySpinning,
                                            'countryFabric': countryFabric,
                                            'countryDyeing': countryDyeing,
                                            'countryMaking': countryMaking,
                                            'fabricProcess': exemple['fabricProcess'],
                                        }

                                        if quality > 0:
                                            json_data['quality'] = round(quality, 2)

                                        if reparability > 0:
                                            json_data['reparability'] = round(reparability, 2)

                                        headers = {
                                            'User-Agent': ragent(),
                                            'accept': 'application/json',
                                            'content-type': 'application/json',
                                        }

                                        try:
                                            response = requests.post('https://ecobalyse.beta.gouv.fr/api/textile/simulator/detailed', headers=headers, json=json_data)
                                        except:
                                            pass

                                        if response.status_code == 200:
                                            df = pd.DataFrame([response.json()])

                                            concatenated_df = pd.concat([concatenated_df, df], ignore_index=True)

                                            count += 1

                                            if count > limit:
                                                # Enregistrement du DataFrame fusionné dans un fichier JSON
                                                output_file = f"data/{textile_type}_{count_file}.json"
                                                concatenated_df.to_json(output_file, orient="records", indent=4)

                                                count = 0
                                                count_file += 1
                                                concatenated_df = pd.DataFrame()

                            
                    mass += increment  # Augmente le poids par pas

            # Enregistrement du DataFrame fusionné dans un fichier JSON
            output_file = f"data/{textile_type}_{count_file}.json"
            concatenated_df.to_json(output_file, orient="records", indent=4)

            break

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        sys.stdout.write('[+] Exit requested')