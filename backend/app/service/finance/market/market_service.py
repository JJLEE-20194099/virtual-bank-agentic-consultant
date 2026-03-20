from app.service.finance.market.vndirect_provider import VNDirectProvider
from app.service.finance.market.gold_provider import GoldProvider
from app.service.finance.market.oil_provider import OilProvider
from vnstock.explorer.misc import *

class MarketService:

    def __init__(self):

        self.stock_provider = VNDirectProvider()
        self.gold_provider = GoldProvider()
        self.oil_provider = OilProvider()

    def get_ohlcv(self, symbol, start_date, end_date, interval):

        return self.stock_provider.get_ohlcv(symbol, start_date, end_date, interval)

    def get_ohlcv_by_length(self, symbol, length, interval):
        return self.stock_provider.get_ohlcv_by_length(symbol, length, interval)

    def get_multiple(self, symbols):
        return self.stock_provider.get_multiple(symbols)

    def get_exchange_rate(self, date):
        data = vcb_exchange_rate(date=date).to_dict(orient='records')
        return data

    def get_domestic_gold_price(self):
        data = {
            "today": self.gold_provider.get_latest(symbols = []),
            "history": self.gold_provider.get_ohlcv_by_length("BT9999NTT", length=30)
        }
        return data
    
    def get_global_gold_price(self):
        data = {
            "today": self.gold_provider.get_latest(symbols = ["XAUUSD"]),
            "history": self.gold_provider.get_ohlcv_by_length("XAUUSD", length=30)
        }
        return data

    def get_global_oil_price(self):
        data = {
            "today": self.oil_provider.get_latest(),
            "history": self.oil_provider.get_ohlcv_by_length(length=30)
        }
        return data
    
    def get_domestic_gold_price_date(self, date):
        data = sjc_gold_price(date).to_dict(orient='records')
        return data

    def get_domestic_oil_price(self):
        data = {
            "today": self.oil_provider.get_domestic_latest(),
            "history": self.oil_provider.get_domestic_ohlcv_by_length("Xăng RON 95-III", length=14)
        }
        return data
    
