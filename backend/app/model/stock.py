from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal, List


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

class StockTransactionBase(BaseModel):
    transaction_id: str 
    customer_id: str 

    datetime: datetime

    stock_code: str 

    action: Literal["buy", "sell"]

    quantity: int = Field(..., gt=0) 
    price: float = Field(..., gt=0)
    fee: float = Field(..., ge=0)    

    @field_validator("stock_code")
    @classmethod
    def normalize_stock(cls, v):
        return v.upper().strip()

    @field_validator("fee", mode="before")
    @classmethod
    def auto_fee(cls, v, info):
        if v is None:
            return 0.0
        return v
    
class StockTransactionCreate(StockTransactionBase):
    pass

class StockTransactionResponse(StockTransactionBase):
    id: int

class StockTransactionBulkCreate(BaseModel):
    transactions: list[StockTransactionCreate]

    @field_validator("transactions")
    @classmethod
    def validate_non_empty(cls, v):
        if len(v) == 0:
            raise ValueError("transactions cannot be empty")
        return v