import random
import uuid
import pandas as pd
from datetime import datetime, timedelta
import os

DATA_PATH = "../raw"
os.makedirs(DATA_PATH, exist_ok=True)

def generate_users(n=1000):
    users = []
    for _ in range(n):
        users.append({
            "user_id": str(uuid.uuid4()),
            "age": random.randint(22, 55),
            "income": random.choice([15000000, 30000000, 50000000]),
            "segment": random.choice(["mass", "affluent"]),
            "has_credit_card": True
        })
    return pd.DataFrame(users)

def generate_transactions(users: pd.DataFrame):
    rows = []
    categories = ["travel", "shopping", "grocery", "rent"]
    for _, u in users.iterrows():
        for _ in range(random.randint(60, 90)):
            cat = random.choice(categories)
            rows.append({
                "trx_id": str(uuid.uuid4()),
                "user_id": u.user_id,
                "category": cat,
                "amount": random.randint(50000, 5000000),
                "installment": random.random() < 0.3,
                "trx_time": datetime.now() - timedelta(days=random.randint(1, 90))
            })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    users = generate_users()
    trx = generate_transactions(users)

    users.to_csv(f"{DATA_PATH}/users.csv", index=False)
    trx.to_csv(f"{DATA_PATH}/transactions.csv", index=False)
