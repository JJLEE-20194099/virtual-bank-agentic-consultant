import random
import uuid
import pandas as pd

def generate_users(n=500_000):
    users = []
    for idx in range(n):
        users.append({
            "user_id": str(uuid.uuid4()),
            "age": random.randint(22, 55),
            "income": random.choice([15e6, 20e6, 30e6, 50e6, 80e6]),
            "has_credit_card": True,
            "segment": random.choice(["mass", "affluent", "premium"])
        })

    return pd.DataFrame(users)


if __name__ == "__main__":
    df = generate_users()
    df.to_parquet("../raw/users.parquet")