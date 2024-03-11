import json

# Charger le fichier JSON
with open('textiles.json') as f:
    data = json.load(f)

# Boucle sur chaque type de textile
for textile_type, exemples in data.items():
    print(f"Type de textile : {textile_type}")
    print("=================================")
    
    # Boucle sur chaque exemple du type de textile
    for exemple in exemples:
        print(f"Nom : {exemple['name']}")

        mass_min, mass_max = exemple['mass']
        mass = mass_min
        while mass < mass_max:
            print(f"Poids (en kg) : {mass:.2f}")

            print("Composition :")
            for material, percentage in exemple['materials'].items():
                print(f" - {material} : {percentage}%")
                
            print(f"Processus de fabrication : {exemple['fabricProcess']}")
            print("\n")

            mass += 0.01  # Augmente le poids par pas de 0.01 kg