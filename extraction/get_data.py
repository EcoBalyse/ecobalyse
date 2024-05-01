#!/usr/bin/env python3
"""
Created on Wed Mar 06 21:28:47 2024.

This script retrieves data from the EcoBalyse API for a given textile type and limit,
and saves the results to JSON files.

"""

# %%
import requests
import sys
import argparse
import json
import pandas as pd
from random import randint
import hashlib

# %%

def readfile(path):
    """Read a file and return a list of lines."""
    if path != None or path != "":
        return [line.strip() for line in open(path, 'r')]
    return

def ragent():
    """Return a random user agent string."""
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
    parser.add_argument("-c", "--cut", help="Textile type cutting files")
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
        limit = 10000
    if args.cut:
        limit_cut = int(args.cut)
    else:
        limit_cut = 10000

    # Load countries data
    df_countries = pd.read_json('/json/countries.json')

    # Load product details data
    with open('/products/products_details.json') as f:
        data = json.load(f)

    # Loop through product types and examples
    for textile_type, examples in data.items():
        if textile_type == arg_textile_type or arg_textile_type == 'all':
            if verbose:
                print(f"Type : {textile_type}")

            concatenated_df = pd.DataFrame()

            count = 0
            count_file = 1
            count_textile_type = 0
            test_exit = False

            for exemple in examples:
                tab_materials = []
                for material, percentage in exemple['materials'].items():
                    tab_materials.append({"id": material, "share": percentage/100})

                if verbose:
                    print(f"Materials : {tab_materials}")

                mass_min, mass_max, increment = exemple['mass']
                mass = mass_min
                while mass <= mass_max:
                    mass = round(mass, 2)
                    if verbose:
                        print(f"Mass : {mass}")

                    for countryMaking in df_countries["code"]:
                        if countryMaking == "---":
                            continue

                        airTransportRatio = 0
                        for low_cost in [False, True]:
                            if low_cost:
                                json_data = {
                                    'mass': mass,
                                    'materials': tab_materials,
                                    'product': textile_type,
                                    'countrySpinning': countryMaking ,
                                    'countryFabric': countryMaking ,
                                    'countryDyeing': countryMaking ,
                                    'countryMaking': countryMaking ,
                                    'fabricProcess': exemple['fabricProcess'],
                                    "makingWaste": None,
                                    "makingDeadStock": None,
                                    "makingComplexity": None,
                                    "yarnSize": None,
                                    "surfaceMass": None,
                                    "disabledSteps": [
                                        "use"
                                    ]
                                }

                                if airTransportRatio > 0:
                                    json_data['airTransportRatio'] = airTransportRatio
                            else:
                                json_data = {
                                    'mass': mass,
                                    'materials': tab_materials,
                                    'product': textile_type,
                                    'countrySpinning': countryMaking ,
                                    'countryFabric': countryMaking ,
                                    'countryDyeing': countryMaking ,
                                    'countryMaking': countryMaking ,
                                    'fabricProcess': exemple['fabricProcess']
                                }

                            headers = {
                                'User-Agent': ragent(),
                                'accept': 'application/json',
                                'content-type': 'application/json',
                            }

                            try:
                                response = requests.post('https://ecobalyse.beta.gouv.fr/api/textile/simulator/detailed', headers=headers, json=json_data)
                            except Exception as e:
                                print("Error ecobalyse.beta.gouv.fr:", e)
                            else:
                                if response.status_code == 200:
                                    # Calculate the MD5 hash of the data structure
                                    json_str = json.dumps(json_data, sort_keys=True)
                                    md5_id = hashlib.md5(json_str.encode()).hexdigest()

                                    # Add the "md5_id" field to the response JSON
                                    response_json = response.json()
                                    response_json['md5_id'] = md5_id

                                    if not low_cost:
                                        airTransportRatio = response_json['lifeCycle'][0]['country']['airTransportRatio']

                                    df = pd.DataFrame([response_json])

                                    concatenated_df = pd.concat([concatenated_df, df], ignore_index=True)

                                    count += 1

                                    if count > limit_cut:
                                        # Save the concatenated DataFrame to a JSON file
                                        output_file = f"/data/{textile_type}_{count_file}.json"
                                        concatenated_df.to_json(output_file, orient="records", indent=4)

                                        count = 0
                                        count_file += 1
                                        concatenated_df = pd.DataFrame()
                                else:
                                    print("Error ecobalyse.beta.gouv.fr status_code:", response.status_code)

                                count_textile_type += 1
                                
                                if count_textile_type >= limit:
                                    test_exit = True
                                    break

                        if test_exit:
                            break

                    if test_exit:
                        break

                    mass += increment  # Increase the mass by the increment value

                if test_exit:
                    if verbose:
                        print(f"Add product : {count_textile_type}")

                    break

            # Save the concatenated DataFrame to a JSON file
            output_file = f"/data/{textile_type}_{count_file}.json"
            concatenated_df.to_json(output_file, orient="records", indent=4)

            if arg_textile_type != 'all':
                break

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        sys.stdout.write('[+] Exit requested')