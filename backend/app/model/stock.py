from pydantic import BaseModel
from typing import List

class Candle(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class Price(BaseModel):
    current: int
    change: int
    changePercent: float

class UnrealizedPnL(BaseModel):
    value: int
    percent: float

class Portfolio(BaseModel):
    totalValue: int
    shares: int
    avgCost: int
    unrealizedPnL: UnrealizedPnL

class Risk(BaseModel):
    score: int
    level: str
    volatility: float
    portfolioExposure: float

class Financials(BaseModel):
    revenue: int
    netIncome: int

class StockResponse(BaseModel):
    symbol: str
    companyName: str
    sector: str
    trend: str
    price: Price
    chart: dict
    portfolio: Portfolio
    risk: Risk
    financials: Financials

