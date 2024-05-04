from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.bash_operator import BashOperator
from docker.types import Mount
import os

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 26),
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'ecobalyse',
    default_args=default_args,
    description='ecobalyse project management',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    tags=['ecobalyse', 'datascientest'],
)

project_patch = os.environ.get('PROJECT_PATH')

# Definition of task_4: Data cleansing and normalization. Testing of different Machine Learning models (pySpark + MLFlow) and storage of MLFlow data.
task_4 = DockerOperator(
    task_id='run_train_model',
    image='ecobalyse-spark',
    container_name='ecobalyse-spark',
    api_version='auto',
    auto_remove='force',
    command='spark-submit /spark/train_model.py',
    environment={
        'DB_USER': os.environ.get('DB_USER'),
        'DB_PASSWORD': os.environ.get('DB_PASSWORD'),
        'DB_CLUSTER': os.environ.get('DB_CLUSTER'),
    },
    docker_url="tcp://docker-proxy:2375",
    network_mode='ecobalyse_vpcbr',
    mount_tmp_dir=False,
    dag=dag,
)

# Defining dependencies between tasks
task_4