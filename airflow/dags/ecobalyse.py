from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ecobalyse',
    default_args=default_args,
    description='ecobalyse project management',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2024, 4, 23),
    catchup=False,
)

task_extraction_run_get_json = BashOperator(
    task_id='extraction_run_get_json',
    bash_command='docker run --rm --name ecobalyse-extract --env-file /opt/requirements/.env -v /opt/requirements/extraction/data:/data -v /opt/requirements/extraction/json:/json -v /opt/requirements/extraction/products:/products ecobalyse-extract python3 /extraction/get_json.py',
    auto_remove=True,
    dag=dag
)

# task_extraction_run_get_json = DockerOperator(
#     task_id='extraction_run_get_json',
#     image='ecobalyse-extract',
#     api_version='auto',
#     auto_remove=True,
#     command='python3 /extraction/get_json.py',
#     volumes=['/opt/requirements/extraction/data:/data',
#              '/opt/requirements/extraction/json:/json',
#              '/opt/requirements/extraction/products:/products'],
#     network_mode='vpcbr',
#     dag=dag
# )

# task_extraction_run_get_data = DockerOperator(
#     task_id='extraction_run_get_data', 
#     image='ecobalyse-extract',
#     api_version='auto',
#     auto_remove=True,
#     command='python3 /extraction/get_data.py -t all',
#     dag=dag,
#     schedule_interval='@monthly'
#     )

# # Tâche 2 qui se lance toutes les heures
# task2 = DummyOperator(task_id='task2', dag=dag, start_date=datetime(2024, 4, 23), schedule_interval=timedelta(hours=1))

# # Tâche commune
# common_task = DummyOperator(task_id='common_task', dag=dag)

# # Liaisons
# task1 >> common_task
# task2 >> common_task