import pandas as pd
from sqlalchemy import create_engine
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../..", "storage", "transactions.db")

FEATURE_STORE = "../../storage/feature_store.json"

def run_feature_job():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    trx = pd.read_sql("transactions", engine)

    features = trx.groupby("user_id").agg(
        total_spend=("amount", "sum"),
        travel_ratio=("category", lambda x: (x=="travel").mean()),
        installment_ratio=("installment", "mean"),
        trx_count=("trx_id", "count")
    ).reset_index()

    store = {row.user_id: row._asdict() for row in features.itertuples()}
    with open(FEATURE_STORE, "w") as f:
        json.dump(store, f, indent=2)

if __name__ == "__main__":
    run_feature_job()
