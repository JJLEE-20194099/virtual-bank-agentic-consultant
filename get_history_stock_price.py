import requests
import json
import time
import os

BASE_URL = "http://localhost:8080/api/v1/market/ohlcv-by-length"
LENGTH = 1000
INTERVAL = "1d"

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
"VCG","VGC","VHC","VIX","VND","VOS","YEG"
]

for stock in stocks:
    try:
        url = f"{BASE_URL}/{stock}?length={LENGTH}&interval={INTERVAL}"
        response = requests.get(url)

        if response.status_code == 200:

            os.makedirs(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/{stock}", exist_ok=True)
            with open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/{stock}/history_price.json", "w", encoding="utf-8") as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=2)


            print(f"Done {stock}")
        else:
            print(f"Failed {stock}: {response.status_code}")

        time.sleep(0.1)

    except Exception as e:
        print(f"Error {stock}: {e}")


print("Saved to history_price.json")