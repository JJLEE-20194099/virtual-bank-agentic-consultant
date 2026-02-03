import pandas as pd
from sqlalchemy import create_engine

DB_URL = "sqlite:///storage/transactions.db"
engine = create_engine(DB_URL)

def ingest_transactions():
    trx = pd.read_csv("../data/raw/transactions.csv")
    trx.to_sql("transactions", engine, if_exists="replace", index=False)

if __name__ == "__main__":
    ingest_transactions()
