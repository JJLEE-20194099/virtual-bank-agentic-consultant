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
import os
from app.core.db_instance import db_client
from app.core.model_instance import model_client
from app.agents.market_analysis_agent import MarketAnalysisAgent

market_analysis_agent = MarketAnalysisAgent()

service = MarketService()

from urllib.parse import urlparse
database_url = os.getenv("DATABASE_URL", "postgresql://swin:swin@localhost:5432/vbac")
parsed = urlparse(database_url)

db_client = PostgresClient(
    user=parsed.username or "swin",
    password=parsed.password or "swin",
    database=parsed.path.lstrip("/") or "vbac",
    host=parsed.hostname or "postgres",
    port=parsed.port or 5432)

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
        0: "short_term",
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

    
    res = requests.get(f"http://localhost:8080/api/v1/user/summary/{user_id}")
    if res.status_code == 200:
        redis_client.set(f"summary:{user_id}", json.dumps(res.json(), default=str), ex=60)

    await db_client.connect()
    data = await db_client.get_stock_transactions_by_user(customer_id = user_id, limit=-1)
    user_df = pd.DataFrame(data)
    user_df["datetime"] = pd.to_datetime(user_df["datetime"], format="mixed")
    user_df = user_df.sort_values("datetime").reset_index(drop=True)
    portfolio = calculate_portfolio(user_df, realtime_prices)
    await db_client.save_portfolio(user_id, portfolio)

    await _update_stock_user_behaviour(user_id)

    res = requests.get(f"http://localhost:8080/api/v1/user/analyze/{user_id}")
    if res.status_code == 200:
        portfolio_advice = res.json()
        await db_client.save_portfolio_advice(user_id, portfolio_advice)


    await db_client.close()


@celery_app.task(name="tasks.update_portfolio")
def update_portfolio(user_id: str):
    asyncio.run(_update_portfolio_async(user_id))


def enrich_context(portfolio: dict, user_type: str) -> dict:
    overall = portfolio["overall"]
    detail = portfolio["detail"]
    market = portfolio["market-news"]

    market_trend = market["trend"]
    market_volatility = market["volatility"]

    market_risk = (
        "high" if market_trend == "bearish" or market_volatility > 25
        else "medium"
    )

    cash_ratio = overall["cash_ratio"]

    cash_status = (
        "low" if cash_ratio < 0.05
        else "high" if cash_ratio > 0.4
        else "normal"
    )


    max_stock = None
    max_pct = 0

    for stock, data in detail.items():
        pct = data["portfolio_summary"]["portfolio_pct"]
        if pct > max_pct:
            max_pct = pct
            max_stock = stock

    concentration_high = max_pct > 0.4


    worst_stock = None
    worst_change = 0

    for stock, data in detail.items():
        change = data["stock_summary"]["data"]["change_percent"]
        if change < worst_change:
            worst_change = change
            worst_stock = stock


    loss_stocks = []
    profit_stocks = []
    high_risk_stocks = []

    for stock, data in detail.items():
        pnl = data["portfolio_summary"]["unrealized_pnl"]
        risk = data["risk"]

        if pnl < 0:
            loss_stocks.append(stock)
        else:
            profit_stocks.append(stock)

        if risk >= 8:
            high_risk_stocks.append(stock)


    unrealized = overall["total_unrealized_pnl"]

    portfolio_health = (
        "bad" if unrealized < 0
        else "good"
    )


    avg_hold = overall["avg_hold_period_days"]
    trading_velocity = overall["trading_velocity"]

    long_term_holder = avg_hold > 90
    active_trader = trading_velocity > 0.5

    portfolio_scale = (
        "large" if overall["total_portfolio_value"] > 100000
        else "normal"
    )


    DAY_GAP = {
        "short_term": (0, 3),
        "swing": (4, 7),
        "long_term": (8, 30)
    }

    min_day, max_day = DAY_GAP[user_type]

    
    insights = {
        "market_condition": market_trend,
        "market_risk": market_risk,
        "volatility": market_volatility,

        "cash_ratio": cash_ratio,
        "cash_status": cash_status,

        "portfolio_health": portfolio_health,
        "portfolio_scale": portfolio_scale,

        "portfolio_concentration": {
            "stock": max_stock,
            "pct": round(max_pct, 2),
            "is_high": concentration_high
        },

        "worst_stock": {
            "stock": worst_stock,
            "change_percent": worst_change
        },

        "loss_stocks": loss_stocks,
        "profit_stocks": profit_stocks,
        "high_risk_stocks": high_risk_stocks,

        "behavior": {
            "long_term_holder": long_term_holder,
            "active_trader": active_trader
        },

        "trading_style": {
            "type": user_type,
            "holding_period_days": f"{min_day}-{max_day}"
        }
    }

    return insights

def rule_engine(features):
    products = set()
    if features["market_risk"] == "high":
        products.update([
            "REBALANCE",
            "STOP_LOSS_SERVICE",
            "PORTFOLIO_INSURANCE",
            "RISK_ALERT_SYSTEM"
        ])

    if features["cash_status"] == "high":
        products.update([
            "IDLE_CASH",
            "CASH_SWEEP",
            "FLEXIBLE_SAVING"
        ])
    elif features["cash_status"] == "low":
        products.update([
            "MARGIN",
            "SMART_MARGIN",
            "CREDIT_LINE"
        ])

    if features["portfolio_health"] == "bad":
        products.update([
            "REBALANCE",
            "STOP_LOSS_SERVICE",
            "COPY_TRADE",
            "MODEL_PORTFOLIO"
        ])

    if features["portfolio_concentration"]["is_high"]:
        products.update([
            "REBALANCE",
            "AUTO_REBALANCE"
        ])

    if features["loss_stocks"]:
        products.update([
            "STOP_LOSS_SERVICE",
            "PORTFOLIO_INSURANCE"
        ])

    if features["high_risk_stocks"]:
        products.update([
            "REBALANCE",
            "RISK_ALERT_SYSTEM"
        ])

    if features["behavior"]["active_trader"]:
        products.update([
            "DAY_TRADING_LIMIT",
            "DERIVATIVES"
        ])

    if features["behavior"]["long_term_holder"]:
        products.update([
            "AUTO_REBALANCE",
            "MODEL_PORTFOLIO",
            "PRIVATE_WEALTH"
        ])


    style = features["trading_style"]["type"]

    if style == "short_term":
        products.update([
            "DAY_TRADING_LIMIT",
            "DERIVATIVES",
            "SMART_MARGIN"
        ])

    elif style == "swing":
        products.update([
            "SMART_MARGIN",
            "COPY_TRADE",
            "MODEL_PORTFOLIO"
        ])

    elif style == "long_term":
        products.update([
            "MODEL_PORTFOLIO",
            "PRIVATE_WEALTH",
            "INVESTMENT_ADVISORY_VIP"
        ])

    if features["portfolio_scale"] == "large":
        products.update([
            "VIP_LOAN",
            "STOCK_BACKED_LOAN",
            "PRIVATE_WEALTH"
        ])

    return list(products)

async def _update_stock_product_recommendation_async(transaction):

    await db_client.connect()
    user_id = transaction["customer_id"]

    BASE_URL = "http://localhost:8080/api/v1/user"

    stock_user_behaviour = await db_client.get_stock_user_behaviour(user_id)

    insight_cluster_dict = {
        1: "short_term",
        0: "swing",
        2: "long_term"
    }

    try:
        user_type = stock_user_behaviour["behaviour_insight"]
    except:
        user_type = insight_cluster_dict[stock_user_behaviour["cluster"]]
  
    url = f"{BASE_URL}/summary/{user_id}"

    res = requests.get(url)
    if res.status_code == 200:

        user_context_data = res.json()

        features = enrich_context(user_context_data, user_type)

        pre_products = rule_engine(features)

        
        data = market_analysis_agent.recommend_stock_product(user_context_data, features, pre_products)

        await db_client.insert_stock_product_recommendation(user_id, data, status = "pending")

        cache_key = f"recommend:{user_id}"
        redis_client.set(
            cache_key,
            json.dumps({
                "user_id": user_id,
                "data": data
            }),
            ex=60 * 60
        )
      


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
        "VCG","VGC","VHC","VIX","VND","VOS","YEG", "PNJ"
        ]


    realtime_prices = await fetch_all(stocks)

    data = {
        f"price:{item['symbol']}": item
        for item in realtime_prices
    }

    path = f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/VN30/history_price.json"
    with open(path, "r", encoding="utf-8") as f:
        vn_30  = json.load(f)[0]
    
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


