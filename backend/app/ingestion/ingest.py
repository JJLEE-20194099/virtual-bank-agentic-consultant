import pandas as pd
import os
from sqlalchemy import create_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "storage", "transactions.db")

engine = create_engine(f"sqlite:///{DB_PATH}")

def ingest_transactions():
    trx = pd.read_csv("../data/raw/transactions.csv")
    trx.to_sql("transactions", engine, if_exists="replace", index=False)

if __name__ == "__main__":
    ingest_transactions()
