from fastapi import APIRouter, Query
from app.service.finance.market.market_service import MarketService
from datetime import datetime
import json
import pandas as pd 
import numpy as np 
from app.core.db_instance import db_client
from app.model.user import StockUserBehaviourBase


router = APIRouter()
service = MarketService()

@router.get(("/summary/{user_id}"))
async def get_stocks_portfolio_summary_by_user_id(user_id: str):
    portfolio_summary = await db_client.get_portfolio(user_id)

    symbols = list(portfolio_summary.keys())

    stock_summaries = await db_client.get_stock_summary_by_symbols(symbols)

    keys = [
        item["symbol"] for item in stock_summaries
    ]


    company_summary = [
       json.load(open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/{key}/summary.json", "r", encoding="utf-8")) for key in keys
    ]

    values = [
        {
            "stock_summary": stock_summaries[i],
            "portfolio_summary": portfolio_summary[key],
            "company_summary": company_summary[i]
        }
        for i, key in enumerate(keys)
    ]

    return dict(zip(keys, values))


@router.get(("/behaviour/{user_id}"))
async def get_stock_behaviour_by_user_id(user_id: str):
    stock_user_behaviour = await db_client.get_stock_user_behaviour(user_id)

    return stock_user_behaviour

@router.post(("/behaviour/create"))
async def save_stock_behaviour(payload: StockUserBehaviourBase):
    data = payload.model_dump()
    await db_client.save_stock_user_behaviour(data["customer_id"], data["behaviour_data"])

    return {"status": "ok"}



@router.post("/behaviour/delete-table/")
async def delete_stock_user_behaviour_table():
    await db_client.delete_stock_user_behaviour_table()

@router.post("/behaviour/delete/{user_id}")
async def delete_stock_user_behaviour(user_id: str):
    await db_client.delete_stock_user_behaviour(user_id = user_id)
    return {"status": "ok"}




