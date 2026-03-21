from fastapi import APIRouter, Query
from app.service.finance.market.market_service import MarketService
from datetime import datetime
import json
import pandas as pd 
import numpy as np 
from app.core.db_instance import db_client
from app.model.stock import StockTransactionCreate, StockTransactionBulkCreate


router = APIRouter()
service = MarketService()

@router.get(("/{user_id}/{symbol}"))
async def get_stock_transactions_by_user_and_stock(user_id: str, symbol: str, limit: int = 20, offset: int = 0):
    return await db_client.get_stock_transactions_by_user_and_stock(customer_id = user_id, stock_code = symbol, limit=limit, offset=offset)

@router.get(("/{user_id}"))
async def get_stock_transactions_by_user(user_id: str, limit: int = 20, offset: int = 0):
    return await db_client.get_stock_transactions_by_user(customer_id = user_id, limit=limit, offset=offset)

@router.post("/transaction")
async def create_transaction(payload: StockTransactionCreate):
    await db_client.insert_stock_transactions([payload.model_dump()])
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


