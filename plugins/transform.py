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
            CASE
                WHEN age < 30 THEN 'young'
                WHEN age BETWEEN 30 AND 50 THEN 'middle'
                ELSE 'senior'
            END AS age_group,
            CASE
                WHEN balance < 0 THEN 'negative'
                WHEN balance <= 1000 THEN 'low'
                ELSE 'high'
            END AS balance_group,
            housing,
            loan,
            contact,
            COUNT(*) AS total_calls,
            SUM((deposit = 'yes')::int) AS success_calls,
            ROUND(
                SUM((deposit = 'yes')::int)::numeric / COUNT(*),
                2
            ) AS success_rate
        FROM stg_banking_raw
        WHERE batch_id = %(batch_id)s
        AND processed_flag = FALSE
        GROUP BY
            age_group,
            balance_group,
            housing,
            loan,
            contact
        ORDER BY success_rate DESC;
        """
        df = pd.read_sql(query, self.engine, params={"batch_id": batch_id})
        return df
