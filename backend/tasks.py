from celery_worker import celery_app
import asyncio
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


