import shutil
import requests
import pandas as pd
import os
from datetime import datetime
AIRFLOW_URL = "http://localhost:8080"
AIRFLOW_USER = "admin"
AIRFLOW_PASS = "admin"
DAG_ID = "banking_etl_pipeline"

class FileIngestService:

    def __init__(self):
        self.data_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../data")
        )

        os.makedirs(self.data_dir, exist_ok=True)

    def _generate_csv_name(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"banking_{timestamp}.csv"

    def save_csv_to_data_dir(self, temp_csv_path: str) -> str:
        csv_filename = self._generate_csv_name()

        host_csv_path = os.path.join(self.data_dir, csv_filename)
        shutil.copy(temp_csv_path, host_csv_path)

        airflow_csv_path = f"/opt/airflow/data/{csv_filename}"
        return airflow_csv_path
    
    def convert_excel_to_csv(self, file_path: str) -> str:
        df = pd.read_excel(file_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"banking_{timestamp}.csv"

        # PATH TRÊN HOST (để ghi file)
        host_csv_path = os.path.join(self.data_dir, csv_filename)
        df.to_csv(host_csv_path, index=False, encoding="utf-8-sig")

        # PATH CHO AIRFLOW (container path)
        airflow_csv_path = f"/opt/airflow/data/{csv_filename}"

        return airflow_csv_path


    def trigger_airflow(self, csv_path: str):
        url = f"{AIRFLOW_URL}/api/v1/dags/{DAG_ID}/dagRuns"

        payload = {
            "conf": {
                "csv_path": csv_path
            }
        }

        res = requests.post(
            url,
            json=payload,
            auth=(AIRFLOW_USER, AIRFLOW_PASS),
            timeout=10
        )

        res.raise_for_status()
