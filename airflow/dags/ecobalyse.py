from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule
from docker.types import Mount
import os

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 24),
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=2),
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

# Définition de task_1
task_1 = DockerOperator(
    task_id='extraction_run_add_product',
    image='ecobalyse-add',
    container_name='ecobalyse-add',
    api_version='auto',
    auto_remove='force',
    command='python3 /app/add_product.py',
    mounts=[
        Mount(target='/json', source=f'{project_patch}/requirements/add_product/json', type='bind'),
    ],
    environment={
        'API_URL': os.environ.get('API_URL'),
        'API_KEY': os.environ.get('API_KEY'),
        'API_KEY_NAME': os.environ.get('API_KEY_NAME'),
    },
    docker_url="tcp://docker-proxy:2375",
    network_mode='ecobalyse_vpcbr',
    mount_tmp_dir=False,
    dag=dag,
)

# Définition de task_2
task_2 = DockerOperator(
    task_id='extraction_run_spark',
    image='ecobalyse-spark',
    container_name='ecobalyse-spark',
    api_version='auto',
    auto_remove='force',
    command='spark-submit /spark/script_spk.py',
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

# Définition de task_3
task_3 = DockerOperator(
    task_id='extraction_run_train_model',
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

# Définition des dépendances entre les tâches
task_1 >> task_2 >> task_3