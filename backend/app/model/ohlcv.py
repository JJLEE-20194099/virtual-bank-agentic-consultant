from pydantic import BaseModel
from datetime import datetime


class OHLCV(BaseModel):

    symbol: str
    time: datetime

    open: float
    high: float
    low: float
    close: float

    volume: float