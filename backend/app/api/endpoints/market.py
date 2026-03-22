from fastapi import APIRouter, Query
from app.service.finance.market.market_service import MarketService
from datetime import datetime
from app.clients.cache import RedisClient
import json
import pandas as pd 
import numpy as np 

router = APIRouter()
service = MarketService()
redis_client = RedisClient()

@router.get("/ohlcv-by-date/{symbol}")
async def get_ohlcv_by_date(
        symbol: str,
        start_date: str = Query(..., description="YYYY-MM-DD"),
        end_date: str = Query("-1", description="-1 for now, or YYYY-MM-DD"),
        interval: str = Query("1d", description="1m, 5m, 15m, 30m, 1h, 1H, 60m, 1d, 1D, d, D, daily, 1w, 1W, w, W, weekly, 1M, m, M, monthly")
    ):

    if end_date == "-1":
        today = datetime.today()
        end_date = today.strftime("%Y-%m-%d") 
    
    return service.get_ohlcv(symbol, start_date, end_date, interval)

@router.get("/ohlcv-by-length/{symbol}")
async def get_history_ohlcv_by_length(
        symbol: str,
        length: int = Query(30, description="Number of data points to retrieve"), 
        interval: str = Query("1d", description="1m, 5m, 15m, 30m, 1h, 1H, 60m, 1d, 1D, d, D, daily, 1w, 1W, w, W, weekly, 1M, m, M, monthly")
    ):

    return service.get_ohlcv_by_length(symbol, length, interval)


@router.get("/stock/summary/{userid}/{symbol}")
async def get_stock_summary(userid: str, symbol: str):

    path = f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/{symbol}/history_price.json"
    with open(path, "r", encoding="utf-8") as f:
        chart_data  = json.load(f)

    path = f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/{symbol}/ohlcv_analysis_data.json"
    with open(path, "r", encoding="utf-8") as f:
        ohlcv_analysis_data  = json.load(f)

    path = f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/portfolio/summary.json"
    with open(path, "r", encoding="utf-8") as f:
        portfolio_summary  = json.load(f)

    path = f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/{symbol}/summary.json"
    with open(path, "r", encoding="utf-8") as f:
        company_info = json.load(f)

    
    return {
        **ohlcv_analysis_data,
        "portfolio": portfolio_summary,
        "company_info": company_info,
        "risk_assessment": 7,
        "ai_stock_analysis": "The stock ...",
        "investment_advice": "Based on the analysis ...",
        "chart_data": chart_data
    }

@router.post("/ohlcv-by-symbols")
async def get_multiple(symbols: list[str]):

    if len(symbols) == 1:
        return redis_client.get(f"price:{symbols[0]}")

    realtime_prices = redis_client.get("realtime_prices:all")
    return [realtime_prices[f"price:{symbol}"] for symbol in symbols]

@router.get("/exchange-rate")
async def get_exchange_rate(date: str = Query(..., description="YYYY-MM-DD")):
    return service.get_exchange_rate(date)

@router.get("/domestic-gold-price-by-date")
async def get_domestic_gold_price_date(date: str = Query(..., description="YYYY-MM-DD")):
    return service.get_domestic_gold_price_date(date)

@router.get("/domestic-gold-price")
async def get_domestic_gold_price():
    return service.get_domestic_gold_price()

@router.get("/global-gold-price")
async def get_global_gold_price():
    return service.get_global_gold_price()
                            
@router.get("/global-oil-price")
async def get_global_oil_price():
    return service.get_global_oil_price()

@router.get("/domestic-oil-price")
async def get_domestic_oil_price():
    return service.get_domestic_oil_price()