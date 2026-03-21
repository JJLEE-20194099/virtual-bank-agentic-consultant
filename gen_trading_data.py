import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta, time
import json

types = ["intraday", "swing", "longterm"]
probs = [0.25, 0.3, 0.45]

n = 1000
labels = np.random.choice(types, size=n, p=probs)

customers = {f"C{i+1:05d}": labels[i] for i in range(n)}

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
"VCG","VGC","VHC","VIX","VND","VOS","YEG"
]

transactions = []
portfolio = {}

start_date = datetime(2023, 7, 3)

MAX_STOCK_HOLD = {
    "intraday": 5,
    "swing": 10,
    "longterm": 20
}


TRADES_PER_DAY = {
    "intraday": (5, 15),
    "swing": (1, 3)
}

DAY_GAP = {
    "intraday": (0, 0),
    "swing": (1, 3),
    "longterm": (5, 30)
}

INTRADAY_CLOSE_PROB = 0.8



def random_time(session, date):
    if session == "morning":
        hour = random.randint(9, 11)
        minute = random.randint(0, 59)
        if hour == 11:
            minute = random.randint(0, 30)
    else:
        hour = random.randint(13, 14)
        minute = random.randint(0, 59)
    return datetime.combine(date.date(), time(hour, minute))

excluded_dates = [
    "2023-09-01", "2023-09-04", "2024-09-03","2023-04-30", '2025-01-01', '2025-01-29', '2026-01-02', '2026-02-17', "2025-01-30",
    "2024-01-01",
    "2024-02-08","2024-02-09","2024-09-02", "2024-02-12","2024-02-13","2024-02-14", '2025-01-27', '2026-02-18','2025-01-27', '2026-02-17','2026-02-19','2026-02-20','2026-02-21','2026-02-22','2025-01-31', '2025-04-07', '2026-01-01',
    "2024-04-18","2024-04-29","2024-04-30",
    "2024-05-01",
    "2024-09-02","2025-04-30", "2025-09-01", "2025-09-02", "2025-05-02", "2025-01-28", "2025-05-01", "2024-01-28", "2024-05-01", "2023-01-28", "2023-05-01", '2025-12-19', '2025-10-30'] + ['2025-11-05', '2025-11-24', '2026-01-27', '2025-11-28', '2025-12-24', '2026-01-13', '2026-01-19', '2025-12-03', '2025-12-29', '2025-11-26', '2025-11-20', '2025-12-09', '2026-02-02', '2025-12-04', '2026-03-03', '2025-12-01', '2025-11-12', '2026-03-06', '2026-03-05', '2026-02-12', '2025-12-08', '2025-10-17', '2025-11-11', '2026-03-11', '2026-01-21', '2026-02-05', '2025-11-17', '2025-12-15', '2025-11-21', '2025-10-28', '2026-02-23', '2025-10-27', '2025-10-24', '2025-10-14', '2025-10-16', '2025-12-22', '2025-10-09', '2025-11-06', '2025-10-31', '2026-01-28', '2025-12-26', '2026-03-13', '2026-02-04', '2026-01-16', '2026-01-23', '2026-03-19', '2026-01-22', '2025-12-18', '2026-02-24', '2025-10-21', '2026-01-20', '2026-02-10', '2025-10-13', '2025-10-22', '2025-12-30', '2026-02-16', '2026-02-09', '2026-01-29', '2025-11-03', '2025-11-19', '2026-03-10', '2026-01-30', '2026-03-04', '2026-01-06', '2026-03-12', '2025-11-10', '2025-11-25', '2025-12-25', '2025-12-23', '2026-03-09', '2026-01-12', '2025-10-23', '2025-10-20', '2026-03-16', '2026-01-15', '2025-11-27', '2026-01-08', '2026-02-26', '2025-12-31', '2025-12-11', '2025-10-10', '2025-11-07', '2026-03-18', '2026-02-11', '2025-10-29', '2025-10-15', '2025-11-04', '2025-11-13', '2025-11-14', '2026-01-09', '2025-12-17', '2026-01-05', '2026-01-14', '2026-01-07', '2025-12-16', '2025-12-12', '2025-12-05', '2026-01-26', '2026-02-06', '2025-11-18', '2025-12-10', '2026-02-03', '2026-03-17', '2026-02-25', '2026-03-02', '2026-02-13', '2025-12-02', '2026-02-27']

def next_trading_day(date):
    date += timedelta(days=1)
    while date.weekday() >= 5 or date.strftime("%Y-%m-%d") in excluded_dates:
        date += timedelta(days=1)
    return date

def advance_trading_days(date, n_days):
    for _ in range(n_days):
        date = next_trading_day(date)
    return date

now = datetime.now()

for cust, style in customers.items():
    current_date = start_date

    held_stocks = set()

    today = datetime.today().date()

    for d in range(300):

        if style != "longterm":
            trades_today = random.randint(*TRADES_PER_DAY[style])
        else:
            if np.random.rand() < 0.2:
                trades_today = 0
            else:
                numbers = [1, 2, 3, 4]
                weights = [0.5, 0.3, 0.15, 0.05] 

                trades_today = random.choices(numbers, weights=weights, k=1)[0]

        intraday_pos = {}

        if current_date.date() > now.date():
            break

        for i in range(trades_today):

            if len(held_stocks) < MAX_STOCK_HOLD[style]:
                stock = random.choice(stocks)
                held_stocks.add(stock)
            else:
                stock = random.choice(list(held_stocks))

            key = (cust, stock)
            qty_holding = portfolio.get(key, 0)

            price = round(np.random.uniform(20, 100), 2)

           
            if style == "intraday":

                if i < trades_today // 2:
                    action = "buy"
                    quantity = random.randint(10, 80)

                    portfolio[key] = qty_holding + quantity
                    intraday_pos[key] = intraday_pos.get(key, 0) + quantity

                    txn_time = random_time("morning", current_date)

                else:
                    if key in intraday_pos and random.random() < INTRADAY_CLOSE_PROB:
                        

                        if intraday_pos[key] == 0:
                            continue

                        sell_type = random.choices(
                            ["partial", "full", "scalp"],
                            weights=[0.5, 0.3, 0.2]
                        )[0]

                        if sell_type == "partial":
                            qty = int(intraday_pos[key] * random.uniform(0.3, 0.7))

                        elif sell_type == "full":
                            qty = intraday_pos[key]
                        else:  
                            qty = int(intraday_pos[key] * random.uniform(0.1, 0.3))

                        quantity = max(1, min(qty, intraday_pos[key]))
                        if quantity == 0:
                            continue
                        
                        action = "sell"

                        portfolio[key] -= quantity
                        intraday_pos[key] = 0

                        txn_time = random_time("afternoon", current_date)
                    else:
                        continue

          
            elif style == "swing":
                action = random.choices(["buy","sell"], [0.6,0.4])[0]

                if action == "buy":
                    quantity = random.randint(10, 120)
                    portfolio[key] = qty_holding + quantity
                else:
                    if qty_holding == 0:
                        continue
                    quantity = random.randint(1, qty_holding)
                    if quantity == 0:
                        continue
                    portfolio[key] -= quantity

                txn_time = random.choice([
                    random_time("morning", current_date),
                    random_time("afternoon", current_date)
                ])

            else:

                if np.random.rand() < 0.2 and trades_today == 0:
                    continue

                action = random.choices(["buy","sell"], [0.7,0.3])[0]

                if action == "buy":
                    quantity = random.randint(20, 200)
                    portfolio[key] = qty_holding + quantity
                else:
                    if qty_holding == 0:
                        continue
                    quantity = random.randint(qty_holding // 2, qty_holding)
                    if quantity == 0:
                        continue
                    portfolio[key] -= quantity

                txn_time = random.choice([
                    random_time("morning", current_date),
                    random_time("afternoon", current_date)
                ])

            fee = price * quantity * random.uniform(0.001, 0.005)

            transactions.append([
                f"T{cust}_{d}_{i}",
                cust,
                txn_time,
                stock,
                action,
                quantity,
                price,
                fee
            ])

        if style == "intraday":
            for key, qty in list(intraday_pos.items()):
                if qty > 0:
                    portfolio[key] -= qty

                    transactions.append([
                        f"T{cust}_{d}_close",
                        cust,
                        random_time("afternoon", current_date),
                        key[1],
                        "sell",
                        qty,
                        round(np.random.uniform(20, 100), 2),
                        0
                    ])

        gap = random.randint(*DAY_GAP[style])
        for _ in range(gap + 1):
            current_date = advance_trading_days(current_date, 1)
           


df = pd.DataFrame(transactions, columns=[
    "transaction_id","customer_id","datetime",
    "stock_code","action","quantity","price","fee"
])

df.to_csv("./synthetic_trading_data.csv", index=False)