from sqlalchemy import create_engine, text
import pandas as pd
import os

class BankingDataExtractor:
    def __init__(self):
        db_url = os.getenv("DW_CONN_STRING")
        self.engine = create_engine(db_url)

    def create_table_if_not_exists(self):
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stg_banking_raw (
                    id SERIAL PRIMARY KEY,
                    age INT,
                    job VARCHAR(50),
                    marital VARCHAR(20),
                    education VARCHAR(50),
                    credit_default VARCHAR(10),
                    balance INT,
                    housing VARCHAR(10),
                    loan VARCHAR(10),
                    contact VARCHAR(20),
                    day INT,
                    month VARCHAR(10),
                    duration INT,
                    campaign INT,
                    pdays INT,
                    previous INT,
                    poutcome VARCHAR(20),
                    deposit VARCHAR(10),
                    batch_id VARCHAR(50),
                    processed_flag BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

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
        self.create_table_if_not_exists()
        self.extract_from_csv(file_path, batch_id)
