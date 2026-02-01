from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime
import pandas as pd

from validateData import BankingDataValidator
from validateFile import FileValidator
from extract import BankingDataExtractor
from transform import BankingDataTransformer
from load import BankingDataLoader
from prepareStaging import BankingDataPrepare

def prepare_staging_task():
    preparer = BankingDataPrepare()
    preparer.prepare_staging()

def validate_task(**context):
    csv_path = context["dag_run"].conf.get("csv_path")
    if not csv_path:
        raise ValueError("csv_path is required")

    validator = FileValidator()
    validator.validate_and_register(csv_path)
    
def extract_task(**context):
    conf = context["dag_run"].conf
    csv_path = conf.get("csv_path")

    if not csv_path:
        raise ValueError("csv_path is required")

    batch_id = context["dag_run"].run_id

    extractor = BankingDataExtractor()
    extractor.run_extract(csv_path, batch_id)


def transform_task(**context):
    batch_id = context["dag_run"].run_id

    transformer = BankingDataTransformer()
    df = transformer.transform(batch_id=batch_id)

    context["ti"].xcom_push(
        key="job_summary",
        value=df.to_json()
    )

def validate_data_task(**context):
    df_json = context["ti"].xcom_pull(
        task_ids="transform",
        key="job_summary"
    )

    batch_id = context["dag_run"].run_id
    df = pd.read_json(df_json)

    validator = BankingDataValidator()
    validator.validate(df, batch_id)

def load_task(**context):
    df_json = context["ti"].xcom_pull(
        task_ids="transform",
        key="job_summary"
    )

    batch_id = context["dag_run"].run_id
    df = pd.read_json(df_json)

    loader = BankingDataLoader()
    loader.load(df, batch_id)
    loader.mark_processed(batch_id)



with DAG(
    dag_id="banking_etl_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,   
    catchup=False,
) as dag:

    start = EmptyOperator(task_id="start")

    validate = PythonOperator(
        task_id="validate_file",
        python_callable=validate_task,
        provide_context=True
    )
    prepare = PythonOperator(
        task_id="prepare_staging",
        python_callable=prepare_staging_task
    )
    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_task,
        provide_context=True
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_task,
        provide_context=True
    )
    validate_data = PythonOperator(
        task_id="validate_data",
        python_callable=validate_data_task,
        provide_context=True
    )
    load = PythonOperator(
        task_id="load",
        python_callable=load_task,
        provide_context=True
    )

    end = EmptyOperator(task_id="end")

    start >> validate >> prepare >> extract >> transform >> validate_data >> load >> end
