import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta, time

# ===== CUSTOMERS =====
customers = {
    "C001": "intraday",
    "C002": "swing",
    "C003": "longterm"
}

# ===== 100 VN STOCKS (subset realistic) =====
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

start_date = datetime(2023, 7, 1)

# ===== LIMIT HOLDING =====
MAX_STOCK_HOLD = {
    "intraday": 5,
    "swing": 10,
    "longterm": 20
}

# ===== TRADING FREQUENCY =====
TRADES_PER_DAY = {
    "intraday": (5, 15),
    "swing": (1, 3),
    "longterm": (0, 2)
}

DAY_GAP = {
    "intraday": (0, 0),
    "swing": (1, 5),
    "longterm": (8, 30)
}

INTRADAY_CLOSE_PROB = 0.8


# ===== HELPER =====
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


def next_trading_day(date):
    date += timedelta(days=1)
    while date.weekday() >= 5:
        date += timedelta(days=1)
    return date

now = datetime.now()

# ===== GENERATE =====
for cust, style in customers.items():
    current_date = start_date

    held_stocks = set()

    today = datetime.today().date()

    for d in range(300):

        trades_today = random.randint(*TRADES_PER_DAY[style])
        intraday_pos = {}

        if current_date.date() > now.date():
            break

        for i in range(trades_today):

            # ===== CHỌN STOCK CÓ GIỚI HẠN SỐ MÃ =====
            if len(held_stocks) < MAX_STOCK_HOLD[style]:
                stock = random.choice(stocks)
                held_stocks.add(stock)
            else:
                stock = random.choice(list(held_stocks))

            key = (cust, stock)
            qty_holding = portfolio.get(key, 0)

            price = round(np.random.uniform(20, 100), 2)

            # ================= INTRADAY =================
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
                        
                        action = "sell"

                        portfolio[key] -= quantity
                        intraday_pos[key] = 0

                        txn_time = random_time("afternoon", current_date)
                    else:
                        continue

            # ================= SWING =================
            elif style == "swing":
                action = random.choices(["buy","sell"], [0.6,0.4])[0]

                if action == "buy":
                    quantity = random.randint(10, 120)
                    portfolio[key] = qty_holding + quantity
                else:
                    if qty_holding == 0:
                        continue
                    quantity = random.randint(1, qty_holding)
                    portfolio[key] -= quantity

                txn_time = random.choice([
                    random_time("morning", current_date),
                    random_time("afternoon", current_date)
                ])

            # ================= LONG TERM =================
            else:
                if trades_today == 0:
                    continue

                action = random.choices(["buy","sell"], [0.85,0.15])[0]

                if action == "buy":
                    quantity = random.randint(20, 200)
                    portfolio[key] = qty_holding + quantity
                else:
                    if qty_holding == 0:
                        continue
                    quantity = random.randint(qty_holding // 2, qty_holding)
                    portfolio[key] -= quantity

                txn_time = random.choice([
                    random_time("morning", current_date),
                    random_time("afternoon", current_date)
                ])

            fee = price * quantity * 0.001

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

        # ===== intraday: force close =====
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

        # ===== next day =====
        gap = random.randint(*DAY_GAP[style])
        for _ in range(gap + 1):
            current_date = next_trading_day(current_date)


df = pd.DataFrame(transactions, columns=[
    "transaction_id","customer_id","datetime",
    "stock_code","action","quantity","price","fee"
])

df.to_csv("./synthetic_trading_data.csv", index=False)