#!/bin/bash


get_request() {
    # Liste des codes pays
    local countries=('AL' 'BD' 'BE' 'CH' 'CN' 'TN' 'TR' 'TW' 'VN')
    # Liste des produits
    local products=('chemise' 'jean' 'jupe' 'manteau' 'pantalon' 'pull' 'tshirt')
     # Liste des matériaux
    local materials=('soie' 'lin-filasse' 'lin-etoupe' 'laine-merinos')
    # Fichier de sortie pour les ventes
    local REQUESTS_FILE="requests.txt"
    
    for product in "${products[@]}" ;
    do
        for country in "${countries[@]}";
        do
            for material in "${materials[@]}"; 
            do
         # Récupérer la requête
            request=$(curl -X GET "https://ecobalyse.beta.gouv?uct=${product}&countryFabric=${country}&countryDyeing=${country}&countryMaking=${country}&fabricProcess=${material}" -H "accept: application/json")
            # Ajouter la requête dans le fichier
            echo "$product - $material -$country: $request" >> "$REQUESTS_FILE"
            done
        done
    done
}

get_request