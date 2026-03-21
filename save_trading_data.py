import pandas as pd
import requests
from datetime import datetime

df = pd.read_csv("/root/code/hackathon/virtual-bank-agentic-consultant/correct_trading_data.csv")

BASE_URL = "http://localhost:8080/api/v1/stock"

df["datetime"] = pd.to_datetime(df["datetime"])

def convert_row(row):
    return {
        "transaction_id": row["transaction_id"],
        "customer_id": row["customer_id"],
        "datetime": row["datetime"].isoformat(),
        "stock_code": row["stock_code"],
        "action": row["action"],
        "quantity": int(row["quantity"]),
        "price": float(row["price"]),
        "fee": float(row["fee"])
    }

payload = {
    "transactions": df.to_dict(orient="records")
}

print("Total:", len(df))



def chunk_list(data, chunk_size=200):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

transactions = [convert_row(r) for _, r in df.iterrows()]

for chunk in chunk_list(transactions, 200):
    res = requests.post(
        f"{BASE_URL}/transaction/bulk",
        json={"transactions": chunk}
    )

    if res.status_code != 200:
        print(res.json())
        print(chunk)
        break