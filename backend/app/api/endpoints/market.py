from fastapi import APIRouter, Query
from app.service.finance.market.market_service import MarketService
from datetime import datetime
import json
import pandas as pd 
import numpy as np 

router = APIRouter()
service = MarketService()


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


def ohlcv_to_df(data):
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], format="mixed")
    df = df.sort_values("time")
    return df

def calculate_price_info(df):
    last_close = df["close"].iloc[-1]
    prev_close = df["close"].iloc[-2]

    change = last_close - prev_close
    change_percent = (change / prev_close) * 100

    return {
        "current": round(last_close, 2),
        "change": round(change, 2),
        "change_percent": round(change_percent, 2)
    }

def calculate_volatility(df):
    df["return"] = df["close"].pct_change()

    volatility = df["return"].std() * np.sqrt(252) * 100  # annualized

    return round(volatility, 2)

def analyze_ohlcv(data):
    df = ohlcv_to_df(data)

    price = calculate_price_info(df)
    volatility = calculate_volatility(df)
    trend = "bearish"

    return {
        **price,
        "volatility": volatility,
        "trend": trend,
    }


@router.get(("/stock/summary/{symbol}"))
async def get_stock_summary(symbol: str):

    path = f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/stock/{symbol}/history_price.json"
    with open(path, "r", encoding="utf-8") as f:
        chart_data  = json.load(f)
    ohlcv_anaysis_data = analyze_ohlcv(chart_data)

    path = f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/portfolio/summary.json"
    with open(path, "r", encoding="utf-8") as f:
        portfolio_summary  = json.load(f)

    

    company_info = {
        "name": "BCM Tập đoàn Đầu tư và Phát triển Công nghiệp Becamex",
        "revenue_billion_vnd": 128000,
        "net_income_billion_vnd": 3200,
        "pe_ratio": 45.2,
        "market_cap_billion_vnd": 132000,
        "dividend_yield_percent": 0.5,
        "sector": "Real Estate"
    }

    return {
        **ohlcv_anaysis_data,
        "portfolio": portfolio_summary,
        "company_info": company_info,
        "risk_assessment": 7,
        "ai_stock_analysis": "The stock ...",
        "investment_advice": "Based on the analysis ...",
        "chart_data": chart_data
    }


@router.post("/ohlcv-by-symbols")
async def get_multiple(symbols: list[str]):
    print(symbols)
    return service.get_multiple(symbols)



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