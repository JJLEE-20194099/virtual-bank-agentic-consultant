import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8080/api/v1/market"

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

def fetch_realtime(symbol):
    url = f"{BASE_URL}/ohlcv-by-symbols"
    res = requests.post(url, json=[symbol])
    if res.status_code == 200:
        data = res.json()[0]

        return {
            "time": datetime.fromtimestamp(data["time"]/1000).isoformat(),
            "open": data["open_price"] / 1000,
            "high": data["high_price"] / 1000,
            "low": data["low_price"] / 1000,
            "close": data["close_price"] / 1000,
            "volume": data["total_trades"]
        }
    return None

def merge_data(old, new):
    existing_times = set(d["time"] for d in old)
    for item in new:
        if item["time"] not in existing_times:
            old.append(item)
    return sorted(old, key=lambda x: x["time"], reverse=True)


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
        print("Fetch realtime today")
        realtime = fetch_realtime(stock)
        if realtime:
            history = merge_data(history, [realtime])

    save_data(file_path, history)
    time.sleep(0.1)
    print(f"Done {stock}", latest_date, has_today)
