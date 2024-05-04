#!/bin/bash
#
#
#

# Récupérer le chemin absolu du répertoire du script (utile pour l'utilisation via crontab)
repertoire=$(cd "$(dirname "$0")" && pwd)

# PATH
EXTRACT_PATH=$repertoire/extraction
SPARK_PATH=$repertoire/spark
REQUIREMENTS_PATH=$repertoire/requirements
API_PATH=$repertoire/api

##################
### Extraction ###
##################

cd $EXTRACT_PATH

# Build des images
docker build -t ecobalyse-extract .

##################
###   Spark    ###
##################

cd $REQUIREMENTS_PATH

mkdir -p extraction/json
mkdir -p extraction/data
mkdir -p mlflow/data/artifacts

cd $SPARK_PATH

# Build des images
docker build -t ecobalyse-spark .

##################
###   Redis    ###
##################

#echo "vm.overcommit_memory = 1" | sudo tee /etc/sysctl.conf
#sudo sysctl "vm.overcommit_memory=1"

##################
###    API     ###
##################

cd $API_PATH

# Build des images
docker build -t ecobalyse-api .
