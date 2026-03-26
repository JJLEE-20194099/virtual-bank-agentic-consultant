
import pandas as pd 
import requests
import json

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

BASE_URL = "http://localhost:8080/api/v1/market"

with open("/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/summary.json", "r", encoding="utf-8") as f:
    company_data = json.load(f)

def match_sector(symbol):
    return company_data[symbol]["sector"]


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

    df["sector"] = df["stock_code"].apply(match_sector)

    sector_values = df.groupby('sector')['transaction_id'].sum().sort_values(ascending=False)
    
    preferred_categories = sector_values.head(3).index.tolist()
    
    user_stocks = list(df.stock_code.unique())
    state = dict(
        zip(
            user_stocks,
            [
                {
                    "shares": 0,
                    "avg_price": 0,
                    "realized_pnl": 0,
                    "buy_queue": []
                }
                for _ in user_stocks
            ]
        )
    )

    total_holding_time = pd.Timedelta(0)
    total_sell_trades = 0

    for _, row in df.iterrows():
        symbol = row["stock_code"]
        qty = row["quantity"]
        price = row["price"]
        side = row["action"]

        time = row["datetime"]
        s = state[symbol]


        if side == "buy":
            total_cost = s["avg_price"] * s["shares"] + price * qty
            s["shares"] += qty
            s["avg_price"] = total_cost / s["shares"]

            s["buy_queue"].append({"qty": qty, "price": price, "time": time})

        elif side == "sell":

            temp_qty = qty
            while temp_qty > 0 and len(s["buy_queue"]):
                buy_node = s["buy_queue"][0]
                sell_qty = min(temp_qty, buy_node["qty"])
                
            
                duration = time - buy_node["time"]
                total_holding_time += duration
                total_sell_trades += 1 
                
                buy_node["qty"] -= sell_qty
                temp_qty -= sell_qty
                if buy_node["qty"] == 0:
                    s["buy_queue"].pop(0)


            pnl = (price - s["avg_price"]) * qty
            s["realized_pnl"] += pnl

            s["shares"] -= qty

            if s["shares"] == 0:
                s["avg_price"] = 0
                s["buy_queue"] = []

    results = {}
    total_portfolio_value = 0
    total_realized_pnl = 0
    total_unrealized_pnl = 0

    for symbol, s in state.items():
        current_price = current_prices[f"price:{symbol}"]["close_price"] / 1000

        if s["shares"] == 0:
            continue

        unrealized = (current_price - s["avg_price"]) * s["shares"]
        total_value = current_price * s["shares"]

        total_portfolio_value += total_value

        total_realized_pnl += s["realized_pnl"]
        total_unrealized_pnl += unrealized

        results[symbol] = {
            "shares": s["shares"],
            "realized_pnl": round(s["realized_pnl"], 2),
            "unrealized_pnl": round(unrealized, 2),
            "total_value": round(total_value, 2),
            "avg_price": round(s["avg_price"], 2),
            "current_price": current_price
        }

    avg_hold_days = (total_holding_time.total_seconds() / 86400) / total_sell_trades if total_sell_trades > 0 else 0

    for symbol in results:
        value = results[symbol]["total_value"]
        pct = (value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
        results[symbol]["portfolio_pct"] = round(pct, 2)
    
    date_range = (df['datetime'].max() - df['datetime'].min()).days
    date_range = max(date_range, 1)
    trading_velocity = len(df) / date_range

    return {
        "portfolio_stats": results,
        "trading_velocity": round(trading_velocity, 2), 
        "avg_hold_period_days": round(avg_hold_days, 2),
        "preferred_categories": preferred_categories,
        "total_portfolio_value": total_portfolio_value,
        "total_realized_pnl": total_realized_pnl,
        "total_unrealized_pnl": total_unrealized_pnl,
    }

