import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../..", "storage", "transactions.db")

FEATURE_STORE = "../../storage/feature_store.json"

def py(v):
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v


def compute_trend(series: pd.Series):
    if len(series) < 2:
        return "stable"
    slope = np.polyfit(range(len(series)), series, 1)[0]
    if slope > 0:
        return "increasing"
    if slope < 0:
        return "decreasing"
    return "stable"


def run_feature_job():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    trx = pd.read_sql("transactions", engine)
    trx["trx_time"] = pd.to_datetime(trx["trx_time"])

    now = datetime.now()
    trx["month"] = trx["trx_time"].dt.to_period("M")

    features = {}

    for user_id, df in trx.groupby("user_id"):
        total_spend = df["amount"].sum()
        avg_spend = df.groupby("month")["amount"].sum().mean()
        spend_std = df.groupby("month")["amount"].sum().std() or 0

        category_ratio = df["category"].value_counts(normalize=True).to_dict()
        top_category = df["category"].value_counts().idxmax()

        monthly_spend = df.groupby("month")["amount"].sum().values
        trend = compute_trend(monthly_spend)

        installment_ratio = df["installment"].mean()
        high_value_ratio = (df["amount"] > 3_000_000).mean()

        recency_days = (now - df["trx_time"].max()).days
        frequency_monthly = len(df) / df["month"].nunique()

        rent_detected = (df["category"] == "rent").mean() > 0.2
        travel_months = df[df["category"] == "travel"]["month"].nunique()

        weekend_ratio = (df["trx_time"].dt.weekday >= 5).mean()

        features[str(user_id)] = {
            "total_spend_3m": py(total_spend),
            "avg_monthly_spend": py(avg_spend),
            "spend_std": py(spend_std),
            "top_category": top_category,
            "category_ratio": {k: py(v) for k, v in category_ratio.items()},
            "trend_3m": trend,
            "installment_ratio": py(installment_ratio),
            "high_value_ratio": py(high_value_ratio),
            "recency_days": py(recency_days),
            "frequency_monthly": py(frequency_monthly),
            "rent_detected": bool(rent_detected),
            "travel_months": py(travel_months),
            "weekend_spend_ratio": py(weekend_ratio)
        }


    with open(FEATURE_STORE, "w") as f:
        json.dump(features, f, indent=2)

if __name__ == "__main__":
    run_feature_job()