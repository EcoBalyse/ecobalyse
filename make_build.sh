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
AIRFLOW_PATH=$repertoire/airflow
ADD_PRODUCT_PATH=$repertoire/add_product

##################
### Extraction ###
##################

cd $EXTRACT_PATH

# Build des images
docker build -t ecobalyse-extract .

###################
### Add Product ###
###################

cd $ADD_PRODUCT_PATH

# Build des images
docker build -t ecobalyse-add .

##################
###   Spark    ###
##################

cd $REQUIREMENTS_PATH

mkdir -p extraction/json
mkdir -p extraction/data
mkdir -p mlflow/data/artifacts
mkdir -p redis/data

cd $SPARK_PATH

# Build des images
docker build -t ecobalyse-spark .

##################
###   Redis    ###
##################

if ! grep -q "vm.overcommit_memory = 1" /etc/sysctl.conf; then
    echo "vm.overcommit_memory = 1" | sudo tee /etc/sysctl.conf
    sudo sysctl "vm.overcommit_memory=1"
fi

##################
###    API     ###
##################

cd $API_PATH

# Build des images
docker build -t ecobalyse-api .

######################
###    AIRFLOW     ###
######################

cd $AIRFLOW_PATH

mkdir -p dags logs plugins

cd $repertoire

airflow_uid="AIRFLOW_UID=$(id -u)"
airflow_gid="AIRFLOW_GID=0"

touch .env

if ! grep -q "^$airflow_uid" .env || ! grep -q "^$airflow_gid" .env; then
    echo -e "\n\n# Airflow Config\n$airflow_uid\n$airflow_gid" >> .env
fi

if ! grep -q "^# Project path" .env; then
    echo -e "\n\n# Project path\nPROJECT_PATH=$repertoire" >> .env
fi

docker-compose up airflow-init