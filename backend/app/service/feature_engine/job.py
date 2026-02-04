import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(
    BASE_DIR, "../..", "storage", "transactions.db"
)

FEAST_DATA_PATH = os.path.join(
    BASE_DIR,
    "./",
    "feature_store",
    "repo",
    "data",
    "user_features.parquet"
)

def py(v):
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v


def compute_trend(series: pd.Series) -> str:
    if len(series) < 2:
        return "stable"

    x = np.arange(len(series))
    y = series.values

    slope = np.polyfit(x, y, 1)[0]

    if slope > 0:
        return "increasing"
    elif slope < 0:
        return "decreasing"
    return "stable"


def run_feature_job():
    
    engine = create_engine(f"sqlite:///{DB_PATH}")
    trx = pd.read_sql("transactions", engine)

    trx["trx_time"] = pd.to_datetime(trx["trx_time"])
    trx["month"] = trx["trx_time"].dt.to_period("M")

    now = datetime.utcnow()
    feature_rows = []

    for user_id, df in trx.groupby("user_id"):
        monthly_spend = df.groupby("month")["amount"].sum()

        total_spend_3m = monthly_spend.sum()
        avg_monthly_spend = monthly_spend.mean()
        spend_std = monthly_spend.std() or 0.0

        category_ratio = df["category"].value_counts(normalize=True).to_dict()
        top_category = df["category"].value_counts().idxmax()

        installment_ratio = df["installment"].mean()
        high_value_ratio = (df["amount"] > 3_000_000).mean().astype(np.float32)

        recency_days = (now - df["trx_time"].max()).days
        frequency_monthly = len(df) / df["month"].nunique()

        travel_months = df[df["category"] == "travel"]["month"].nunique()
        weekend_spend_ratio = (df["trx_time"].dt.weekday >= 5).mean()

        trend_3m = compute_trend(monthly_spend)

        rent_detected = (df["category"] == "rent").mean() > 0.2

        feature_rows.append({
            "user_id": str(user_id),
            "event_timestamp": now,

            "total_spend_3m": py(total_spend_3m),
            "avg_monthly_spend": py(avg_monthly_spend),
            "spend_std": py(spend_std),

            "installment_ratio": py(installment_ratio),
            "high_value_ratio": py(high_value_ratio),

            "frequency_monthly": py(frequency_monthly),
            "recency_days": py(recency_days),

            "travel_months": py(travel_months),
            "weekend_spend_ratio": py(weekend_spend_ratio),
            "top_category": top_category,
            "category_ratio_json": json.dumps({k: py(v) for k, v in category_ratio.items()}),
            "trend_3m": trend_3m,
            "rent_detected": rent_detected
        })

    feature_df = pd.DataFrame(feature_rows)

    os.makedirs(os.path.dirname(FEAST_DATA_PATH), exist_ok=True)

    feature_df.to_parquet(FEAST_DATA_PATH, index=False)

    print(f"Feature job completed. Rows: {len(feature_df)}")


if __name__ == "__main__":
    run_feature_job()
