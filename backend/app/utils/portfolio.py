
import pandas as pd 
import requests

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

BASE_URL = "http://localhost:8080/api/v1/market"


def fetch_realtime(symbols):
    url = f"{BASE_URL}/ohlcv-by-symbols"
    res = requests.post(url, json=symbols)
    if res.status_code == 200:
        data = res.json()

        data = [
            {
                "realtime_price": item["close_price"] / 1000,
                "symbol": item["symbol"]
            } for item in data
        ]
    
        return dict(zip(
            [item["symbol"] for item in data],
            [item["realtime_price"] for item in data]
        ))
    return {}


def calculate_portfolio(df, current_prices):
    portfolio = {}

    
    user_stocks = list(df.stock_code.unique())
    state = dict(
        zip(
            user_stocks,
            [
                {
                    "shares": 0,
                    "avg_price": 0,
                    "realized_pnl": 0
                }
                for _ in user_stocks
            ]
        )
    )

    for _, row in df.iterrows():
        symbol = row["stock_code"]
        qty = row["quantity"]
        price = row["price"]
        side = row["action"]

        s = state[symbol]


        if side == "buy":
            total_cost = s["avg_price"] * s["shares"] + price * qty
            s["shares"] += qty
            s["avg_price"] = total_cost / s["shares"]

        elif side == "sell":
            pnl = (price - s["avg_price"]) * qty
            s["realized_pnl"] += pnl

            s["shares"] -= qty

            if s["shares"] == 0:
                s["avg_price"] = 0

    results = {}
    total_portfolio_value = 0

    for symbol, s in state.items():
        current_price = current_prices[f"price:{symbol}"]["close_price"] / 1000

        if s["shares"] == 0:
            continue

        unrealized = (current_price - s["avg_price"]) * s["shares"]
        total_value = current_price * s["shares"]

        total_portfolio_value += total_value

        results[symbol] = {
            "shares": s["shares"],
            "realized_pnl": round(s["realized_pnl"], 2),
            "unrealized_pnl": round(unrealized, 2),
            "total_value": round(total_value, 2),
            "avg_price": round(s["avg_price"], 2),
            "current_price": current_price
        }

    for symbol in results:
        value = results[symbol]["total_value"]
        pct = (value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
        results[symbol]["portfolio_pct"] = round(pct, 2)

    return results

