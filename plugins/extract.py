from sqlalchemy import create_engine, text
import pandas as pd
import os

class BankingDataExtractor:
    def __init__(self):
        db_url = os.getenv("DW_CONN_STRING")
        self.engine = create_engine(db_url)

    
    def extract_from_csv(self, file_path, batch_id):
        df = pd.read_csv(file_path)

        df.rename(columns={"default": "credit_default"}, inplace=True)
        df["batch_id"] = batch_id

        with self.engine.begin() as conn:
            df.to_sql(
                "stg_banking_raw",
                conn,
                if_exists="append",
                index=False,
                method="multi"
            )

    def run_extract(self, file_path, batch_id):
        self.extract_from_csv(file_path, batch_id)
