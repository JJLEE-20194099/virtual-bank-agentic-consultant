import random
import pandas as pd
from datetime import datetime, timedelta

MCC = {
    "travel": ["3000", "3001"],
    "shopping": ["5000", "5001"],
    "grocery": ["5411"],
    "rent": ["6513"]
}

def generate_transactions(users, months=3):
    trx = []
    for _, u in users.iterrows():
        num_trx = random.randint(60, 90)
        for _ in range(num_trx):
            category = random.choice(list(MCC.keys()))
            trx.append({
                "trx_id": random.randint(1e9, 1e10),
                "user_id": u.user_id,
                "amount": random.randint(50_000, 5_000_000),
                "mcc": random.choice(MCC[category]),
                "category": category,
                "trx_time": datetime.now() - timedelta(days=random.randint(1, 90)),
                "installment": random.random() < 0.3
            })
    return pd.DataFrame(trx)
