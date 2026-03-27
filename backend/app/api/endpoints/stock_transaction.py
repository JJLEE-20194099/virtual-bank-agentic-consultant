from fastapi import APIRouter, Query, BackgroundTasks
from app.service.finance.market.market_service import MarketService
import json
import pandas as pd 
import numpy as np 
from app.core.db_instance import db_client
from app.model.stock import StockTransactionCreate, StockTransactionBulkCreate, StockBuySellBase, SimulateStockBuySellBase
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
import random
from tasks import update_portfolio, update_stock_product_recommendation

from app.clients.cache import RedisClient
redis_client = RedisClient()

from celery import chain

router = APIRouter()
service = MarketService()

@router.get(("/{user_id}/{symbol}"))
async def get_stock_transactions_by_user_and_stock(user_id: str, symbol: str, limit: int = 20, offset: int = 0):
    return await db_client.get_stock_transactions_by_user_and_stock(customer_id = user_id, stock_code = symbol, limit=limit, offset=offset)

@router.get(("/{user_id}"))
async def get_stock_transactions_by_user(user_id: str, limit: int = 20, offset: int = 0):
    return await db_client.get_stock_transactions_by_user(customer_id = user_id, limit=limit, offset=offset)


@router.post("/buy-sell-simulation")
async def simulate_buysell_stock(payload: SimulateStockBuySellBase):

    realtime_prices = redis_client.get("realtime_prices:all")

    dt_str = payload.datetime
    simulation_date = datetime.fromisoformat(dt_str) \
    .replace(tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")) \
    .replace(microsecond=0, tzinfo=None)

    fee_rate = random.uniform(0.001, 0.005)

    if payload.price == -1:
        payload.price = realtime_prices[f"price:{payload.stock_code}"]["close_price"] / 1000

    fee = payload.quantity * payload.price * fee_rate

    transaction_id = f"{payload.customer_id}_{payload.stock_code}_{simulation_date.isoformat()}"
    transaction = {
        "transaction_id": transaction_id,
        "customer_id": payload.customer_id,
        "datetime": simulation_date,
        "stock_code": payload.stock_code,
        "action": payload.action,
        "quantity": payload.quantity,
        "price": payload.price,
        "fee": fee
    }

    await db_client.insert_stock_transactions([transaction])

    update_portfolio.delay(payload.customer_id)

    update_stock_product_recommendation.delay(transaction)

    # Write recommend product here
    
    return {"status": "ok", "transaction_id": transaction_id}


@router.post("/buy-sell")
async def buysell_stock(payload: StockBuySellBase):

    redis_client.delete(f"summary:{payload.customer_id}")

    realtime_prices = redis_client.get("realtime_prices:all")

    now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(microsecond=0, tzinfo=None)
    fee_rate = random.uniform(0.001, 0.005)

    if payload.price == -1:
        payload.price = realtime_prices[f"price:{payload.stock_code}"]["close_price"] / 1000

    fee = payload.quantity * payload.price * fee_rate

    transaction_id = f"{payload.customer_id}_{payload.stock_code}_{now.isoformat()}"
    transaction = {
        "transaction_id": transaction_id,
        "customer_id": payload.customer_id,
        "datetime": now,
        "stock_code": payload.stock_code,
        "action": payload.action,
        "quantity": payload.quantity,
        "price": payload.price,
        "fee": fee
    }

    await db_client.insert_stock_transactions([transaction])


    if payload.action == "sell":
        stock_pnl_info = await db_client.get_stock_info_portfolio(payload.customer_id, payload.stock_code)
        user_info = await db_client.get_user(payload.customer_id)

        user_info["available_cash"] += stock_pnl_info["shares"] * stock_pnl_info["current_price"]
        await db_client.insert_user(payload.customer_id, user_info)
    

    update_portfolio.delay(payload.customer_id)
    update_stock_product_recommendation.delay(transaction)
    
    return {"status": "ok", "transaction_id": transaction_id}
    

@router.post("/transaction")
async def create_transaction(payload: StockTransactionCreate):
    await db_client.insert_stock_transactions([payload.model_dump()])
    return {"status": "ok"}

@router.post("/transaction/delete/{transaction_id}")
async def delete_transaction(transaction_id: str):
    await db_client.delete_stock_transaction(transaction_id = transaction_id)
    return {"status": "ok"}


@router.post("/transaction/bulk")
async def create_transactions(payload: StockTransactionBulkCreate):
    await db_client.insert_stock_transactions(
        [t.model_dump() for t in payload.transactions]
    )
    return {
        "status": "ok",
        "count": len(payload.transactions)
    }


