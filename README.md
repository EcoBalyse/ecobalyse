# Projet Ecobalyse

Projet Ecobalyse effectué dans le cadre de la Formation Data Engineer de DataScientest

Projet Réalisé par :

- Yajing HOU

- Bertrand LECLERCQ

- Kenza DIEYE

## ORIGINE DU PROJET :

Démarche qui existe depuis 2021, prend son origine dans la loi Climat et Résilience, elle-même issue du travail de la Convention Citoyenne pour le Climat. Logiciel open-source développé au sein d'une startup d'État. 

L’objectif du projet est d'accélérer la mise en place de l'affichage environnemental et proposer un outil permettant aux industriels de mieux comprendre l’impact de leur production sur l’environnement.

## NOTRE OBJECTIF :

Mieux comprendre l’empreinte environnementale d’une base de données produits :

- Automatisation

- Analyses multivariées

- Analyse prédictive

## ARCHITECTURE :

Le projet se découpe suivant cette arborescence :

- add_product

- airflow

- api

- extraction

- mlflow-custom

- requirements

- spark

### ADD_PRODUCT

Conteneur Docker contenant un script python d'ajout de nouveau produit (Appel à notre API)

### AIRFLOW

Le répertoire dags contient les trois DAG utilisés par Airflow :

- ecobalyse_extract.py : extraction des données à partir de l'API Officielle Ecobalyse (https://ecobalyse.beta.gouv.fr/#/api)

- ecobalyse_training.py : ajout de nouveaux produits + entrainement du modèle de Machine Learning

- ecobalyse.py : ajout de nouveaux produits + statistiques via pySpark (traitement long) + entrainement du modèle de Machine Learning

### API

Conteneur Docker contenant notre API (FastAPI). Cette API fait appel à une base externe MongoDB Atlas et utilise un cache REDIS. Certaines routes seront protégées par une clé d'API

Voici quelques requêtes d'example :

#### Vérifier que l'API est fonctionnelle
curl -X GET -i http://localhost:8000/

#### Vider cache Redis
curl -X GET -i http://localhost:8000/cache/clear

#### Affichage de la liste "poducts"
curl -X GET -i "http://localhost:8000/product" -H 'access_token: YOUR_API_KEY' -H 'Content-Type: application/json'

#### Affichage des produits "jean"
curl -X GET -i "http://localhost:8000/product/jean" -H 'access_token: YOUR_API_KEY' -H 'Content-Type: application/json'

#### Affichage des produits "chemise" fabriqués en Chine (CN)
curl -X GET -i "http://localhost:8000/product/chemise/CN" -H 'access_token: YOUR_API_KEY' -H 'Content-Type: application/json'

#### Affichage Good product "manteau"
curl -X GET -i "http://localhost:8000/product/manteau/good_product" -H 'access_token: YOUR_API_KEY' -H 'Content-Type: application/json'

#### Affichage Bad product "tshirt"
curl -X GET -i "http://localhost:8000/product/tshirt/bad_product" -H 'access_token: YOUR_API_KEY' -H 'Content-Type: application/json'

#### Stats Spark
curl -X GET -i "http://localhost:8000/stats/countries" -H 'access_token: YOUR_API_KEY' -H 'Content-Type: application/json'
curl -X GET -i "http://localhost:8000/stats/days_of_wear" -H 'access_token: YOUR_API_KEY' -H 'Content-Type: application/json'
curl -X GET -i "http://localhost:8000/stats/impacts" -H 'access_token: YOUR_API_KEY' -H 'Content-Type: application/json'
curl -X GET -i "http://localhost:8000/stats/outliers" -H 'access_token: YOUR_API_KEY' -H 'Content-Type: application/json'
curl -X GET -i "http://localhost:8000/stats/ranking" -H 'access_token: YOUR_API_KEY' -H 'Content-Type: application/json'

#### Ajout d'un produit
curl -X POST "http://localhost:8000/product" \
 -H 'access_token: YOUR_API_KEY'\
 -H "content-type: application/json" \
 -d '{"mass": 0.17, "materials": [{"id": "ei-coton", "share": 1, "country": "FR"}], "product": "tshirt", "countrySpinning": "FR", "countryFabric": "FR", "countryDyeing": "FR", "countryMaking": "FR", "fabricProcess": "knitting-mix"}'

#### Suppression d'un produit
curl -X DELETE "http://localhost:8000/product?md5_id=15a853d8fc6bee14a946559190111f51" \
     -H 'access_token: YOUR_API_KEY' \
     -H "content-type: application/json"

#### Prédiction d'un produit
curl -X POST "http://localhost:8000/predict" \
     -H 'access_token: YOUR_API_KEY' \
     -H "content-type: application/json" \
     -d '{"ProductId":"pantalon","MaterialId_1":"ei-coton-organic","MaterialId_2":"ei-pet","MaterialId_1_share":0.7,"MaterialId_2_share":0.3,"CountryDyeingCode":"BD","CountryFabricCode":"BD","CountryMakingCode":"BD","FabricProcess":"knitting-mix","Mass":0.2,"AirTransportRatio":0.33}'

### EXTRACTION

Conteneur Docker permettant d'effectuer l'extraction des données à partir de l'API Officielle ecobalyse. Les 4 scripts Python sont utilisés par le DAG ecobalyse_extract.

### MLFLOW-CUSTOM

Conteneur Docker qui nous permet de personnaliser le conteneur officiel de MLFlow

### SPARK

Conteneur Docker qui permet d'effectuer des statisitiques et d'entrainer nos modèles de Machine Learning

- script_spk.py : utilisation de pySpark pour créer 5 collections dans notre base de données MongoDB Atlas (stats_countries / stats_days_of_wear / stats_impacts / stats_outliers / stats_ranking)

- train_model.py : première version pour l'entrainement de nos modèles en utilisant pySpark ML

- train_model_bis.py : seconde version optimisée et c'est celle que nous avons retenu. Elle enregistre les informations dans MLFlow.

## PREREQUIS

Vous devez avoir une machine permettant d'exécuter un script bash et de lancer des conteneurs Docker. De plus, Airflow et Spark sont assez gourmand donc une machine disposant une mémoire RAM suffisante.

## INSTALLATION

La première chose à faire est de récupérer le projet :

git clone git@github.com:EcoBalyse/ecobalyse.git

Ensuite, vous devez créer une base de données MongoDB Atlas : https://www.mongodb.com/cloud/atlas/register

Dans MongoDB Atlas, pensez à mettre votre adresse IP dans la whitelist : section "Network Access"

Vous devrez paramétrer ce nouveau compte pour une utilisation via PyMongo

Une fois que vous avez vos identifiants de connexion à la base de données MongoDB, vous pouvez copier le fichier .env.example en .env

Dans ce fichier .env, vous aurez deux sections à renseigner :

- les paramètres de la base MongDB Atlas

- les paramètres de l'API (FastAPI)

Une fois que tout cela sera effectué, voici les commandes qui seront à exécuter :

./make_build.sh

Une fois terminé, il faudra lancer :

docker-compose up -d

Si vous souhaitez arrêter le projet :

docker-compose down

Une fois que tout est lancé, voici les différentes url :

- Airflow : http://mon_ip:8080

- API : http://mon_ip:8000/docs

- MLFlow : http://mon_ip:5000

## COPYRIGHT

Ce projet a été effectué dans le cadre de la formation Data Engineer de DataScientest. La propriété intellectuelle revient à :

- Yajing HOU

- Bertrand LECLERCQ

- Kenza DIEYE

Pour exploiter ou modifier le projet, veuillez contacter contact@bl-dev.fr