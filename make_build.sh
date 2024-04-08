#!/bin/bash
#
#
#

# Récupérer le chemin absolu du répertoire du script (utile pour l'utilisation via crontab)
repertoire=$(cd "$(dirname "$0")" && pwd)

# PATH
EXTRACT_PATH=$repertoire/extraction
SPARK_PATH=$repertoire/spark
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

cd $SPARK_PATH

# Build des images
docker build -t ecobalyse-spark .
