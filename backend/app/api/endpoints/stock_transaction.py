from fastapi import APIRouter, Query
from app.service.finance.market.market_service import MarketService
import json
import pandas as pd 
import numpy as np 
from app.core.db_instance import db_client
from app.model.stock import StockTransactionCreate, StockTransactionBulkCreate, StockBuySellBase
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
import random


router = APIRouter()
service = MarketService()

@router.get(("/{user_id}/{symbol}"))
async def get_stock_transactions_by_user_and_stock(user_id: str, symbol: str, limit: int = 20, offset: int = 0):
    return await db_client.get_stock_transactions_by_user_and_stock(customer_id = user_id, stock_code = symbol, limit=limit, offset=offset)

@router.get(("/{user_id}"))
async def get_stock_transactions_by_user(user_id: str, limit: int = 20, offset: int = 0):
    return await db_client.get_stock_transactions_by_user(customer_id = user_id, limit=limit, offset=offset)

@router.post("/buy-sell")
async def buysell_stock(payload: StockBuySellBase):

    now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(microsecond=0, tzinfo=None)
    fee_rate = random.uniform(0.001, 0.005)
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


