import pandas as pd
import json
import os
import random
from datetime import datetime

DATA_DIR = "/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock"

price_cache = {}

def load_price(stock):
    if stock in price_cache:
        return price_cache[stock]

    path = os.path.join(DATA_DIR, stock, "history_price.json")

    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        data = json.load(f)

    price_map = {}
    for d in data:
        date = datetime.fromisoformat(d["time"]).strftime("%Y-%m-%d")
        price_map[date] = d["close"]  

    price_cache[stock] = price_map
    return price_map

def add_noise(base_price):
    noise = random.randint(-4000, 4000) / 1000 
    return round(max(0.1, base_price + noise), 2)

dates = []
def fix_prices(df):
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

    new_prices = []

    grouped = df.sort_values("datetime").groupby(["stock_code", "date"])

    for (stock, date), group in grouped:
        price_map = load_price(stock)
        date_str = str(date)

        if date_str not in price_map:
            print(f"Missing price {stock} {date}")
            dates.append(date)
            base_price = None
        else:
            base_price = price_map[date_str]

        first_price = None

        for i, row in group.iterrows():
            if base_price is None:
                new_price = row["price"]  
            else:
                if first_price is None:
                    new_price = base_price
                    first_price = new_price
                else:
                    new_price = add_noise(first_price)

            new_prices.append((i, new_price))


    for idx, price in new_prices:
        df.at[idx, "price"] = price

    return df.drop(columns=["date"])


df = pd.read_csv("./synthetic_trading_data.csv")

customers = df["customer_id"].unique()
dfs = []
for customer in customers:
    # print(f"Fixing prices for customer {customer}...")
    cust_df = df[df["customer_id"] == customer]
    cust_df = cust_df.reset_index(drop=True)
    cust_df = fix_prices(cust_df)
    dfs.append(cust_df)
 
final_df = pd.concat(dfs).reset_index(drop=True)

def apply_fee(value):
    return value * random.uniform(0.001, 0.005)

final_df["fee"] = final_df["price"] * final_df["quantity"]
final_df["fee"] = final_df["fee"].apply(apply_fee)

final_df.to_csv("./correct_trading_data.csv", index=False)

print(list(set(dates)))