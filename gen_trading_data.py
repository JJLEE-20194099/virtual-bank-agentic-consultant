import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta, time
import json


types = ["short_term", "swing", "long_term"]
probs = [0.4, 0.35, 0.25]

n_customers = 1000
labels = np.random.choice(types, size=n_customers, p=probs)
customers = {f"C{i+1:05d}": labels[i] for i in range(n_customers)}

with open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/customer/behaviour_labels.json", "w", encoding="utf-8") as f:
    json.dump(customers, f, ensure_ascii=False, indent=2)

stocks = [
"ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG",
"MBB","MSN","MWG","PLX","POW","SAB","SSI","STB","TCB","TPB",
"VCB","VHM","VIB","VIC","VJC","VNM","VPB","VRE",
"AAA","ANV","ASM","BCG","BSI","BMP","CII","CMG","CSM",
"CSV","DBC","DCM","DGC","DIG","DPM","DXG","EVF","FRT","GEX",
"GMD","HAH","HSG","IDC","IJC","KBC","KDH","LPB","MBS","MSB",
"NKG","NLG","NT2","OCB","PAN","PC1","PDR","PET","PHR","PVD",
"PVS","PVT","REE","SBT","SHB","SJS","SZC","TCH","TCM","TNG",
"VCG","VGC","VHC","VIX","VND","VOS","YEG", "PNJ"
]


start_date = datetime(2024, 7, 3)

excluded_dates = set([
    "2023-09-01", "2023-09-04", "2024-09-03","2023-04-30", '2025-01-01', '2025-01-29', '2026-01-02', '2026-02-17', "2025-01-30",
    "2024-01-01",
    "2024-02-08","2024-02-09","2024-09-02", "2024-02-12","2024-02-13","2024-02-14", '2025-01-27', '2026-02-18','2025-01-27', '2026-02-17','2026-02-19','2026-02-20','2026-02-21','2026-02-22','2025-01-31', '2025-04-07', '2026-01-01',
    "2024-04-18","2024-04-29","2024-04-30",
    "2024-05-01",
    "2024-09-02","2025-04-30", "2025-09-01", "2025-09-02", "2025-05-02", "2025-01-28", "2025-05-01", "2024-01-28", "2024-05-01", "2023-01-28", "2023-05-01", '2025-12-19', '2025-10-30'] + ['2025-11-05', '2025-11-24', '2026-01-27', '2025-11-28', '2025-12-24', '2026-01-13', '2026-01-19', '2025-12-03', '2025-12-29', '2025-11-26', '2025-11-20', '2025-12-09', '2026-02-02', '2025-12-04', '2026-03-03', '2025-12-01', '2025-11-12', '2026-03-06', '2026-03-05', '2026-02-12', '2025-12-08', '2025-10-17', '2025-11-11', '2026-03-11', '2026-01-21', '2026-02-05', '2025-11-17', '2025-12-15', '2025-11-21', '2025-10-28', '2026-02-23', '2025-10-27', '2025-10-24', '2025-10-14', '2025-10-16', '2025-12-22', '2025-10-09', '2025-11-06', '2025-10-31', '2026-01-28', '2025-12-26', '2026-03-13', '2026-02-04', '2026-01-16', '2026-01-23', '2026-03-19', '2026-01-22', '2025-12-18', '2026-02-24', '2025-10-21', '2026-01-20', '2026-02-10', '2025-10-13', '2025-10-22', '2025-12-30', '2026-02-16', '2026-02-09', '2026-01-29', '2025-11-03', '2025-11-19', '2026-03-10', '2026-01-30', '2026-03-04', '2026-01-06', '2026-03-12', '2025-11-10', '2025-11-25', '2025-12-25', '2025-12-23', '2026-03-09', '2026-01-12', '2025-10-23', '2025-10-20', '2026-03-16', '2026-01-15', '2025-11-27', '2026-01-08', '2026-02-26', '2025-12-31', '2025-12-11', '2025-10-10', '2025-11-07', '2026-03-18', '2026-02-11', '2025-10-29', '2025-10-15', '2025-11-04', '2025-11-13', '2025-11-14', '2026-01-09', '2025-12-17', '2026-01-05', '2026-01-14', '2026-01-07', '2025-12-16', '2025-12-12', '2025-12-05', '2026-01-26', '2026-02-06', '2025-11-18', '2025-12-10', '2026-02-03', '2026-03-17', '2026-02-25', '2026-03-02', '2026-02-13', '2025-12-02', '2026-02-27'])

DAY_GAP = {
    "short_term": (0, 3),
    "swing": (4, 7),
    "long_term": (8, 30)
}

TRADES_PER_DAY = {
    "short_term": (5, 10),
    "swing": (2, 5),
    "long_term": (0, 2)
}

MAX_STOCK_HOLD = {
    "short_term": 5,
    "swing": 10,
    "long_term": 20
}

HOLDING_RANGE = {
    "short_term": (2, 3),
    "swing": (5, 10),
    "long_term": (10, 60)
}

prob_new_stock = {
    "short_term": 0.6,
    "swing": 0.4,
    "long_term": 0.2
}

SELL_RATIO = {
    "short_term": 0.6,
    "swing": 0.5,
    "long_term": 0.3
}



portfolio = {}   
buy_lots = {}    
transactions = []



def is_trading_day(date):
    return date.weekday() < 5 and date.strftime("%Y-%m-%d") not in excluded_dates


def next_trading_day(date):
    date += timedelta(days=1)
    while not is_trading_day(date):
        date += timedelta(days=1)
    return date


def advance_days(date, n):
    for _ in range(n):
        date = next_trading_day(date)
    return date


def random_time(date):
    session = random.choice(["morning", "afternoon"])

    if session == "morning":
        hour = random.randint(9, 11)
        minute = random.randint(0, 59)
        if hour == 11:
            minute = random.randint(0, 30)

    else:
        hour = random.randint(13, 14)
        minute = random.randint(0, 45)

    return datetime.combine(date.date(), time(hour, minute))


def eligible_to_sell(lots, current_date):
    result = []
    for d, q, hold in lots:
        days = (current_date.date() - d.date()).days
        if days >= 2 and days >= hold:
            result.append((d, q, hold))
    return result


def sell_fifo(key, qty, current_date):
    lots = buy_lots.get(key, [])
    new_lots = []
    remaining = qty

    for d, q, hold in lots:
        days = (current_date.date() - d.date()).days

        if days < 2:
            new_lots.append((d, q, hold))
            continue

        if remaining == 0:
            new_lots.append((d, q, hold))
            continue

        if q <= remaining:
            remaining -= q
        else:
            new_lots.append((d, q - remaining, hold))
            remaining = 0

    buy_lots[key] = new_lots


now = datetime.now()

for cust, style in customers.items():

    current_date = start_date

    for day in range(300):

        if current_date > now:
            break

        if not is_trading_day(current_date):
            current_date = next_trading_day(current_date)
            continue

        trades_today = random.randint(*TRADES_PER_DAY[style])

        for _ in range(trades_today):

            held_stocks = {
                s for (c, s), q in portfolio.items()
                if c == cust and q > 0
            }

            sellable_stocks = [
                s for (c, s), lots in buy_lots.items()
                if c == cust and eligible_to_sell(lots, current_date)
            ]

            action = random.choices(["buy", "sell"], [0.6, 0.4])[0]

            price = round(np.random.uniform(20, 100), 2)

          
            if action == "sell" and sellable_stocks:

                stock = random.choice(sellable_stocks)
                key = (cust, stock)

                lots = eligible_to_sell(buy_lots[key], current_date)
                max_qty = sum(q for _, q, _ in lots)

                qty = random.randint(1, max_qty)

                portfolio[key] -= qty
                sell_fifo(key, qty, current_date)

                transactions.append([
                    f"T{cust}_{day}_SELL_{_}",
                    cust,
                    random_time(current_date),
                    stock,
                    "sell",
                    qty,
                    price,
                    price * qty * 0.001
                ])

        
            else:

                if len(held_stocks) < MAX_STOCK_HOLD[style]:
                    if random.random() < prob_new_stock[style]:
                        stock = random.choice(stocks)
                    else:
                        stock = random.choice(list(held_stocks)) if held_stocks else random.choice(stocks)
                else:
                    stock = random.choice(list(held_stocks))

                key = (cust, stock)

                qty = random.randint(10, 120)
                hold_days = random.randint(*HOLDING_RANGE[style])

                portfolio[key] = portfolio.get(key, 0) + qty

                buy_lots.setdefault(key, []).append((current_date, qty, hold_days))

                transactions.append([
                    f"T{cust}_{day}_BUY_{_}",
                    cust,
                    random_time(current_date),
                    stock,
                    "buy",
                    qty,
                    price,
                    price * qty * 0.001
                ])


        gap = random.randint(*DAY_GAP[style])
        current_date = advance_days(current_date, gap + 1)

    print("Done", cust, style)


df = pd.DataFrame(transactions, columns=[
    "transaction_id","customer_id","datetime",
    "stock_code","action","quantity","price","fee"
])

df.to_csv("/root/code/hackathon/virtual-bank-agentic-consultant/synthetic_trading_data.csv", index=False)