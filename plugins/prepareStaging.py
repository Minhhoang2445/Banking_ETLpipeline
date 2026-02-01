from sqlalchemy import create_engine, text
import pandas as pd
import os

class BankingDataPrepare:
    def __init__(self):
        db_url = os.getenv("DW_CONN_STRING")
        self.engine = create_engine(db_url)

    def prepare_staging(self):
        query = """
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
        """
        create_index_sql = """
            CREATE INDEX IF NOT EXISTS idx_stg_banking_unprocessed
            ON stg_banking_raw (batch_id)
            WHERE processed_flag = FALSE;
            """
        with self.engine.begin() as conn:
            conn.execute(text(query))
            conn.execute(text(create_index_sql))