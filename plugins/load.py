from sqlalchemy import create_engine, text
import os


class BankingDataLoader:
    def __init__(self):
        db_url = os.getenv("DW_CONN_STRING")
        self.engine = create_engine(db_url)

    def create_mart_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS mart_job_campaign_summary (
            job VARCHAR(50),
            total_calls INT,
            success_calls INT,
            success_rate NUMERIC(5,2),
            batch_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.engine.begin() as conn:
            conn.execute(text(query))

    def load(self, df, batch_id):
        self.create_mart_table()

        required_cols = {"job", "total_calls", "success_calls", "success_rate"}
        if not required_cols.issubset(df.columns):
            raise ValueError("DataFrame thiếu cột cần thiết")

        df["batch_id"] = batch_id

        with self.engine.begin() as conn:
            conn.execute(
                text("DELETE FROM mart_job_campaign_summary WHERE batch_id = :batch_id"),
                {"batch_id": batch_id}
            )

            df.to_sql(
                "mart_job_campaign_summary",
                conn,
                if_exists="append",
                index=False,
                method="multi"
            )
