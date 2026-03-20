from fastapi import APIRouter, Query
from app.service.finance.market.market_service import MarketService
from datetime import datetime

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



@router.post("/ohlcv-by-symbols")
async def get_multiple(symbols: list[str]):
    print(symbols)
    return service.get_multiple(symbols)


@router.get("/exchange-rate")
async def get_exchange_rate(date: str = Query(..., description="YYYY-MM-DD")):
    return service.get_exchange_rate(date)

@router.get("/sjc-gold-price")
async def get_sjc_gold_price(date: str = Query(..., description="YYYY-MM-DD")):
    return service.get_sjc_gold_price(date)
