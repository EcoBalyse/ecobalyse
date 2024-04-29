from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.bash_operator import BashOperator
from docker.types import Mount
import os

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 24),
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'ecobalyse_extract',
    default_args=default_args,
    description='ecobalyse project management',
    schedule_interval='0 3 1 * *',
    catchup=False,
    tags=['ecobalyse', 'datascientest'],
)

project_patch = os.environ.get('PROJECT_PATH')

# Definition of task_1: json extraction from the ecobalyse api
task_1 = DockerOperator(
    task_id='extraction_run_get_json',
    image='ecobalyse-extract',
    container_name='ecobalyse-extract',
    api_version='auto',
    auto_remove='force',
    command='python3 /extraction/get_json.py',
    mounts=[
        Mount(target='/json', source=f'{project_patch}/requirements/extraction/json', type='bind'),
    ],
    docker_url="tcp://docker-proxy:2375",
    network_mode='ecobalyse_vpcbr',
    mount_tmp_dir=False,
    dag=dag,
)

# Definition of task_2: extracting data from the ecobalyse api
task_2 = DockerOperator(
    task_id='extraction_run_get_data',
    image='ecobalyse-extract',
    container_name='ecobalyse-extract',
    api_version='auto',
    auto_remove='force',
    command='python3 /extraction/get_data.py -t all',
    mounts=[
        Mount(target='/data', source=f'{project_patch}/requirements/extraction/data', type='bind'),
        Mount(target='/json', source=f'{project_patch}/requirements/extraction/json', type='bind'),
        Mount(target='/products', source=f'{project_patch}/requirements/extraction/products', type='bind'),
    ],
    docker_url="tcp://docker-proxy:2375",
    network_mode='ecobalyse_vpcbr',
    mount_tmp_dir=False,
    dag=dag,
)

# Definition of task_3: creation of mongodb collections and data import
task_3 = DockerOperator(
    task_id='extraction_run_create_mongodb',
    image='ecobalyse-extract',
    container_name='ecobalyse-extract',
    api_version='auto',
    auto_remove='force',
    # command='python3 /extraction/create_mongodb.py -i',
    command='python3 /extraction/create_mongodb.py',
    mounts=[
        Mount(target='/data', source=f'{project_patch}/requirements/extraction/data', type='bind'),
        Mount(target='/json', source=f'{project_patch}/requirements/extraction/json', type='bind'),
        Mount(target='/products', source=f'{project_patch}/requirements/extraction/products', type='bind'),
    ],
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

# Definition of task_4: creation of the mongodb collection for documentation on impact criteria
task_4 = DockerOperator(
    task_id='extraction_run_doc_collection',
    image='ecobalyse-extract',
    container_name='ecobalyse-extract',
    api_version='auto',
    auto_remove='force',
    command='python3 /extraction/create_doc_collection.py',
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

# Definition of task_5: Redis cache cleanup
task_5 = BashOperator(
    task_id='clear_cache',
    bash_command='curl -X GET -i http://api:8000/cache/clear',
    dag=dag,
)

# Defining dependencies between tasks
task_1 >> task_2 >> task_3 >> task_4 >> task_5