from fastapi import APIRouter, Query
from app.service.finance.market.market_service import MarketService
from datetime import datetime
import json
import pandas as pd 
import numpy as np 
from app.core.db_instance import db_client


router = APIRouter()
service = MarketService()

@router.get(("/summary/{user_id}"))
async def get_stocks_by_user_id(user_id: str):
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







