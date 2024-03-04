# CADRAGE :

## Contexte :
Démarche quii existe depuis 2013, prend son origine dans la loi Climat et Résilience, elle-même issue du travail de la Convention Citoyenne pour le Climat.
Logiciel open-source développé au sein d'une startup d'État.
Objectif : accélérer la mise en place de l'affichage environnemental.

## Périmètre :
Deux secteurs : les produits textiles et les produits alimentaires.

## Public Cible (qui va utiliser notre produit) :
Toutes les entreprises souhaitant calculer gratuitement et rapidement leurs impacts environnementaux sans nécessiter l'intervention d'experts en Analyse du Cycle de Vie.

# EXPLORATION :

## Source de données :
La base de données actuellement utilisée par Ecobalyse est la Base Impacts développée par l’ADEME. D’autres bases de données de référence sont utilisées dans l’industrie telles que celles développées par Ecoinvent, Sphera (Gabi), Bureau Veritas (Codde) l’Union Européenne (PEF), Quantis, la Sustainable Apparel Coalition (Higg Index), etc. 
Dans le cadre de la mise en place du dispositif français d’affichage environnemental, Ecobalyse est en lien avec l’ADEME pour mettre en place une base de données enrichie et spécifique au secteur Textile. Ces réflexions intègrent notamment la possibilité de rendre cette base de données dynamique afin de retranscrire au fil de l'eau les dernières connaissances sectorielles.

## Description :
Ecobalyse permet de calculer les impacts environnementaux de produits textiles et alimentaires, en agissant sur différentes étapes du cycle de vie.

## Type de connexion :
Le logiciel fonctionne en tant que logiciel open-source. Connexion API au format OpenAPI.

## Lien de connexion à la données :
https://ecobalyse.beta.gouv.fr/api

## Documentation
https://ecobalyse.beta.gouv.fr/#/api

## Plage temporelle des données dispo :
(à compléter)

## Architecture :
(à compléter)

### Requettes (comment atteindre la donnée) :
wget https://ecobalyse.beta.gouv.fr/api
cat api | jq .


### Exemple de données :
(à compléter)
type de produit textile
la saisie de sa masse et de sa composition
