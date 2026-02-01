from sqlalchemy import create_engine
import pandas as pd
import os


class BankingDataTransformer:
    def __init__(self):
        db_url = os.getenv("DW_CONN_STRING")
        self.engine = create_engine(db_url)

    def transform(self, batch_id):
        query = """
        SELECT
            job,
            COUNT(*) AS total_calls,
            SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) AS success_calls,
            ROUND(
                SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END)::numeric / COUNT(*),
                2
            ) AS success_rate
        FROM stg_banking_raw
        WHERE batch_id = %(batch_id)s
        AND processed_flag = FALSE
        GROUP BY job
        ORDER BY success_rate DESC;
        """


        df = pd.read_sql(query, self.engine, params={"batch_id": batch_id})
        return df
