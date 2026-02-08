import random
import uuid
import pandas as pd
from datetime import datetime, timedelta
import os

DATA_PATH = "../raw"
os.makedirs(DATA_PATH, exist_ok=True)


MONTHS = 3
TODAY = datetime.now()

CATEGORY_CONFIG = {
    "travel": (2_000_000, 8_000_000),
    "shopping": (500_000, 5_000_000),
    "grocery": (200_000, 1_500_000),
    "rent": (8_000_000, 15_000_000),
    "entertainment": (300_000, 2_000_000)
}

ARCHETYPES = {
    "TRAVEL_LOVER": {
        "category_weight": {
            "travel": 0.45,
            "shopping": 0.25,
            "grocery": 0.15,
            "entertainment": 0.15
        },
        "installment_ratio": 0.2,
        "monthly_trx": (25, 35)
    },
    "FAMILY_SETTLED": {
        "category_weight": {
            "rent": 0.35,
            "grocery": 0.35,
            "shopping": 0.2,
            "entertainment": 0.1
        },
        "installment_ratio": 0.3,
        "monthly_trx": (20, 30)
    },
    "INSTALLMENT_DEP": {
        "category_weight": {
            "shopping": 0.4,
            "electronics": 0.2,
            "grocery": 0.2,
            "entertainment": 0.2
        },
        "installment_ratio": 0.7,
        "monthly_trx": (30, 40)
    },
    "IMPULSIVE": {
        "category_weight": {
            "shopping": 0.5,
            "entertainment": 0.3,
            "travel": 0.2
        },
        "installment_ratio": 0.6,
        "monthly_trx": (35, 45)
    },
    "WEALTHY_STABLE": {
        "category_weight": {
            "travel": 0.3,
            "shopping": 0.3,
            "rent": 0.2,
            "grocery": 0.2
        },
        "installment_ratio": 0.1,
        "monthly_trx": (20, 25)
    },
    "BUDGET_DIGITAL": {
        "category_weight": {
            "grocery": 0.4,
            "shopping": 0.3,
            "entertainment": 0.3
        },
        "installment_ratio": 0.2,
        "monthly_trx": (40, 55)
    },
    "BALANCED": {
        "category_weight": {
            "travel": 0.2,
            "shopping": 0.3,
            "grocery": 0.3,
            "entertainment": 0.2
        },
        "installment_ratio": 0.3,
        "monthly_trx": (25, 35)
    }
}


def generate_users(n=1000):
    users = []
    archetypes = list(ARCHETYPES.keys())

    for _ in range(n):
        archetype = random.choice(archetypes)
        users.append({
            "user_id": str(uuid.uuid4()),
            "age": random.randint(23, 55),
            "income": random.choice([15_000_000, 30_000_000, 50_000_000, 80_000_000]),
            "segment": random.choice(["mass", "affluent"]),
            "archetype": archetype,
            "has_credit_card": True
        })

    return pd.DataFrame(users)


def random_date_in_month(month_offset):
    start = TODAY - timedelta(days=30 * month_offset)
    return start - timedelta(days=random.randint(0, 29))

def generate_transactions(users: pd.DataFrame):
    transactions = []

    for _, user in users.iterrows():
        profile = ARCHETYPES[user.archetype]

        for m in range(MONTHS):
            trx_count = random.randint(*profile["monthly_trx"])

            for _ in range(trx_count):
                category = random.choices(
                    population=list(profile["category_weight"].keys()),
                    weights=list(profile["category_weight"].values())
                )[0]

                amount_range = CATEGORY_CONFIG.get(
                    category, (500_000, 3_000_000)
                )

                amount = random.randint(*amount_range)
                is_installment = random.random() < profile["installment_ratio"]

                installment_data = {
                    "status": False,
                    "info": {}
                }

                if is_installment:
                    total_months = random.choice([3, 6, 9, 12])
                    current_month = random.randint(1, total_months)
                    interest_rate = random.choice([0, 1, 2, 3, 5])

                    installment_amount = int(
                        amount * (1 + interest_rate / 100) / total_months
                    )

                    installment_data = {
                        "status": True,
                        "info": {
                            "current_installment_month": current_month,
                            "total_installment_month": total_months,
                            "interest_rate": interest_rate,
                            "installment_amount": installment_amount
                        }
                    }

                transactions.append({
                    "trx_id": str(uuid.uuid4()),
                    "user_id": user.user_id,
                    "category": category,
                    "amount": amount,
                    "installment": installment_data,
                    "trx_time": random_date_in_month(m)
                })
    

    transactions["installment"] = transactions["installment"].apply(json.dumps)

    return pd.DataFrame(transactions)

if __name__ == "__main__":
    users = generate_users()
    trx = generate_transactions(users)

    users.to_csv(f"{DATA_PATH}/users.csv", index=False)
    trx.to_csv(f"{DATA_PATH}/transactions.csv", index=False)

    print(users["archetype"].value_counts())
