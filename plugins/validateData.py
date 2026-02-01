

import os
import pandas as pd
from sqlalchemy import create_engine


class BankingDataValidator:
    required_columns = [
        "age_group",
        "balance_group",
        "housing",
        "loan",
        "contact",
        "total_calls",
        "success_calls",
        "success_rate"
    ]
    def validate(self, df, batch_id):
        if df.empty:
            raise ValueError(
                f"Batch {batch_id} không có dữ liệu sau transform")

        missing = [c for c in self.required_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Thiếu cột: {', '.join(missing)}")

        for col in ["total_calls", "success_calls", "success_rate"]:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise TypeError(f"Cột '{col}' phải là kiểu số")

        if (df["total_calls"] < 0).any():
            raise ValueError("total_calls không được âm")

        if (df["success_calls"] < 0).any():
            raise ValueError("success_calls không được âm")

        if (df["success_calls"] > df["total_calls"]).any():
            raise ValueError("success_calls không được lớn hơn total_calls")

        if ((df["success_rate"] < 0) | (df["success_rate"] > 1)).any():
            raise ValueError("success_rate phải nằm trong [0,1]")
        return True
