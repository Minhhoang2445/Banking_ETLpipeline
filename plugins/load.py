from sqlalchemy import create_engine, text
import os


class BankingDataLoader:
    def __init__(self):
        db_url = os.getenv("DW_CONN_STRING")
        self.engine = create_engine(db_url)

    def create_mart_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS campaign_summary (
            age_group VARCHAR(50),
            balance_group VARCHAR(50),
            housing VARCHAR(50),
            loan VARCHAR(50),
            contact VARCHAR(50),
            total_calls INT,
            success_calls INT,
            success_rate NUMERIC(5,2),
            batch_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.engine.begin() as conn:
            conn.execute(text(query))
    
    def mark_processed(self, batch_id):
        query = """
        UPDATE stg_banking_raw
        SET processed_flag = TRUE
        WHERE batch_id = :batch_id
        AND processed_flag = FALSE
        """
        with self.engine.begin() as conn:
            conn.execute(text(query), {"batch_id": batch_id})

    def load(self, df, batch_id):
        self.create_mart_table()

        required_cols = {"age_group", "balance_group", "housing", "loan", "contact", "total_calls", "success_calls", "success_rate"}
        if not required_cols.issubset(df.columns):
            raise ValueError("DataFrame thiếu cột cần thiết")

        df["batch_id"] = batch_id

        with self.engine.begin() as conn:
            conn.execute(
                text("DELETE FROM campaign_summary WHERE batch_id = :batch_id"),
                {"batch_id": batch_id}
            )

            df.to_sql(
                "campaign_summary",
                conn,
                if_exists="append",
                index=False,
                method="multi"
            )
