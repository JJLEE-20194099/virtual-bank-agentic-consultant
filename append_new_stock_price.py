import requests
import json
from datetime import datetime, timedelta
import time
import os
import pandas as pd
import numpy as np
import asyncio
from backend.app.clients.db import PostgresClient

from backend.app.clients.cache import RedisClient

BASE_URL = "http://localhost:8080/api/v1/market"


redis_client = RedisClient()    
realtime_prices =  redis_client.get("realtime_prices:all")

def load_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_latest_date(data):
    if not data:
        return None
    dates = [datetime.fromisoformat(d["time"]) for d in data]
    return max(dates)

def fetch_missing_history(symbol, start_date):
    url = f"{BASE_URL}/ohlcv-by-date/{symbol}"
    params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": "-1",
        "interval": "1d"
    }
    res = requests.get(url, params=params)
    if res.status_code == 200:
        return res.json()
    return []

def format_realtime_data(data):
    
    return {
        "time": datetime.fromtimestamp(data["time"]/1000).isoformat(),
        "open": data["open_price"] / 1000,
        "high": data["high_price"] / 1000,
        "low": data["low_price"] / 1000,
        "close": data["close_price"] / 1000,
        "volume": data["total_trades"]
        }


def detect_trend(df):
    close = df["close"]
    
    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()

    last_close = close.iloc[-1]

    if ma20.iloc[-1] < ma50.iloc[-1]:
        trend = "bearish"
    else:
        trend = "bullish"

    recent_high = df["high"].iloc[-10:-1].max()
    
    if trend == "bearish":
        if last_close > recent_high:
            state = "reversal_confirmed"
        elif last_close > ma20.iloc[-1]:
            state = "potential_reversal"
        else:
            state = "downtrend_continuation"
    else:
        state = "uptrend"

    return trend, state

def calculate_price_info(df):
    last_close = df["close"].iloc[-1]
    prev_close = df["close"].iloc[-2]

    change = last_close - prev_close
    if prev_close == 0 or pd.isna(prev_close):
        change_percent = 0.0
    else:
        change_percent = (change / prev_close) * 100


    trend, state = detect_trend(df)

    return {
        "current": round(last_close, 2),
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "trend": trend,
        "current_state": state
    }

def calculate_volatility(df):
    df["return"] = df["close"].pct_change()

    volatility = df["return"].std() * np.sqrt(252) * 100 

    return round(volatility, 2)

def ohlcv_to_df(data):
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], format="mixed")
    df = df.sort_values("time")
    return df

def analyze_ohlcv(data):
    df = ohlcv_to_df(data)

    price = calculate_price_info(df)
    volatility = calculate_volatility(df)

    return {
        **price,
        "volatility": volatility,
    }


def merge_data(old, new):
    existing_times = set(d["time"] for d in old)
    for item in new:
        if item["time"] not in existing_times:
            old.append(item)
    return sorted(old, key=lambda x: x["time"], reverse=True)


stocks = [
"VN30",
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

db_client = PostgresClient(
    user="swin",
    password="swin",
    database="vbac",
    host="localhost"
)

async def run():

    await db_client.connect()
    await db_client.init_stock_summary_table()

    for stock in stocks:

        file_path = f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/{stock}/history_price.json"
        history = load_data(file_path)

        today = datetime.now().date()

        latest = get_latest_date(history)

        if latest:
            latest_date = latest.date()
            if latest_date < today - timedelta(days=1):
                print(f"Missing history from {latest_date}")
                missing_data = fetch_missing_history(stock, latest_date + timedelta(days=1))
                history = merge_data(history, missing_data)
        else:
            print("No data, skip or fetch full")

        has_today = any(
            datetime.fromisoformat(d["time"]).date() == today
            for d in history
        )

        if not has_today:
            realtime = None
            if stock != "VN30":
                realtime = format_realtime_data(realtime_prices[f"price:{stock}"])
            else:
                url = f"{BASE_URL}/ohlcv-by-length/VN30?length=1&interval=1d"
                res = requests.get(url)
                if res.status_code == 200:
                    realtime = res.json()[0]
                    


            if realtime:
                history = merge_data(history, [realtime])

        save_data(file_path, history)
        ohlcv_analysis_data = analyze_ohlcv(history)

        os.makedirs(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/{stock}", exist_ok=True)
        with open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/{stock}/ohlcv_analysis_data.json", "w", encoding="utf-8") as f:
            json.dump(ohlcv_analysis_data, f, ensure_ascii=False, indent=2)

        await db_client.save_stock_summary(stock, ohlcv_analysis_data)

        time.sleep(0.1)
        print(f"Done {stock}", latest_date, has_today)



if __name__ == "__main__":
    asyncio.run(run())