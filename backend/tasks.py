from celery_worker import celery_app
import asyncio
import requests
from app.clients.db import PostgresClient
from app.clients.cache import RedisClient
from app.utils.portfolio import calculate_portfolio, fetch_realtime, stocks
from app.service.finance.market.market_service import MarketService
import pandas as pd
import json
from datetime import datetime
from app.utils.feature_engine import make_cluster_features
from app.core.model_instance import model_client

from app.core.db_instance import db_client
from app.core.model_instance import model_client
from app.agents.market_analysis_agent import MarketAnalysisAgent

market_analysis_agent = MarketAnalysisAgent()

service = MarketService()

db_client = PostgresClient(
    user="swin",
    password="swin",
    database="vbac",
    host="localhost"
)

redis_client = RedisClient()

with open("/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/summary.json", "r", encoding="utf-8") as f:
    company_data = json.load(f)

def match_sector(symbol):
    return company_data[symbol]["sector"]

async def _update_stock_user_behaviour(user_id: str):
    data = await db_client.get_stock_transactions_by_user(customer_id = user_id, limit=-1)
    user_df = pd.DataFrame(data)

    user_df["sector"] = user_df["stock_code"].apply(match_sector)

    scaled_test_features, behaviour_feature_data = make_cluster_features(user_df)


    cluster = model_client.loaded_model.predict(scaled_test_features)[0]

    behaviour_feature_data = behaviour_feature_data[0]

    behaviour_feature_data["cluster"] = (int)(cluster)

    insight_cluster_dict = {
        1: "short_term",
        0: "swing",
        2: "long_term"
    }

    behaviour_feature_data = {
        "behaviour_insight":  insight_cluster_dict[cluster],
        **behaviour_feature_data
    }

    await db_client.save_stock_user_behaviour(user_id, behaviour_feature_data)

    return behaviour_feature_data


async def _update_portfolio_async(user_id: str):

    realtime_prices = redis_client.get("realtime_prices:all")

    await db_client.connect()
    data = await db_client.get_stock_transactions_by_user(customer_id = user_id, limit=-1)
    user_df = pd.DataFrame(data)
    user_df["datetime"] = pd.to_datetime(user_df["datetime"], format="mixed")
    user_df = user_df.sort_values("datetime").reset_index(drop=True)
    portfolio = calculate_portfolio(user_df, realtime_prices)
    await db_client.save_portfolio(user_id, portfolio)

    await _update_stock_user_behaviour(user_id)


    await db_client.close()


@celery_app.task(name="tasks.update_portfolio")
def update_portfolio(user_id: str):
    asyncio.run(_update_portfolio_async(user_id))


def enrich_context(portfolio: dict) -> dict:
    overall = portfolio["overall"]
    detail = portfolio["detail"]
    market = portfolio["market-news"]

    max_stock = None
    max_pct = 0

    for stock, data in detail.items():
        pct = data["portfolio_summary"]["portfolio_pct"]
        if pct > max_pct:
            max_pct = pct
            max_stock = stock

    worst_stock = None
    worst_change = 0

    for stock, data in detail.items():
        change = data["stock_summary"]["data"]["change_percent"]
        if change < worst_change:
            worst_change = change
            worst_stock = stock

    insights = {
        "market_condition": market["trend"],
        "market_risk": "high" if market["trend"] == "bearish" else "medium",
        "cash_ratio": overall["cash_ratio"],
        "cash_status": (
            "low" if overall["cash_ratio"] < 0.05 else
            "high" if overall["cash_ratio"] > 0.4 else
            "normal"
        ),
        "portfolio_concentration": {
            "stock": max_stock,
            "pct": round(max_pct, 2),
            "is_high": max_pct > 0.4
        },
        "worst_stock": {
            "stock": worst_stock,
            "change_percent": worst_change
        },
        "portfolio_scale": (
            "large" if overall["total_portfolio_value"] > 100000 else "normal"
        )
    }

    return {
        **portfolio,
        "insights": insights
    }

async def _update_stock_product_recommendation_async(transaction):

    await db_client.connect()
    user_id = transaction["customer_id"]

    BASE_URL = "http://localhost:8080/api/v1/user"

    url = f"{BASE_URL}/summary/{user_id}"
   
    res = requests.get(url)
    if res.status_code == 200:
        user_context_data = enrich_context(res.json())
        data = market_analysis_agent.recommend_stock_product(user_context_data)

        await db_client.insert_stock_product_recommendation(user_id, data, status = "pending")
        return data
    return {}


@celery_app.task(name="tasks.update_stock_product_recommendation")
def update_stock_product_recommendation(transaction):
    asyncio.run(_update_stock_product_recommendation_async(transaction))



async def fetch_batch(batch):
    return service.get_multiple(batch)


async def fetch_all(stocks):
    tasks = []
    batch_size = 10
    for i in range(0, len(stocks), batch_size):
        tasks.append(fetch_batch(stocks[i:i+batch_size]))
    results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]

async def _update_realtime_price_async():
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


    realtime_prices = await fetch_all(stocks)

    data = {
        f"price:{item['symbol']}": item
        for item in realtime_prices
    }

    path = f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/VN30/history_price.json"
    with open(path, "r", encoding="utf-8") as f:
        vn_30  = json.load(f)[0]["close"]
    
    data["price:VN30"] = vn_30
    
    redis_client.set(
        "realtime_prices:all",
        json.dumps(data),
        ex=60 * 60 * 24
    )

    redis_client.set_many(data, ex=60 * 60 * 24)

    sample = realtime_prices[0]

    print(sample["symbol"], sample["close_price"], datetime.fromtimestamp(sample["time"] / 1000))

    return "Cache Realtime Prices price:symbol & realtime_prices:all"

@celery_app.task(name="tasks.update_realtime_price")
def update_realtime_price():
    asyncio.run(_update_realtime_price_async())


