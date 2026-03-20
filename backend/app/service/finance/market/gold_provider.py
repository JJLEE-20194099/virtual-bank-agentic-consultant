import httpx
import datetime
from typing import List, Optional
from app.config.query import GOLD_PROVIDER_NAME

BASE_URL = "https://www.vang.today/api"

class GoldProvider:

    def __init__(self):
        self.client = httpx.Client(timeout=10)

    def get_ohlcv_by_length(self, symbol: str, length: int = 30, interval:str = "1d"):
        url = f"{BASE_URL}/prices"
        params = {
            "type": symbol,  
            "days": length
        }
        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        items = resp.json()["history"]

        ohlcv_list = []
        for item in items:
            ohlcv_list.append({
                "time": item["date"],
                "close": item["prices"][symbol]["buy"]
            })
        return ohlcv_list

    def get_latest(self, symbols = []):
        url = f"{BASE_URL}/prices?action=current"
        params = {
        }
        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        items = resp.json()["prices"]

        data = [{
                "symbol": item_key,
                "provider": items[item_key]["name"],
                "buy_price": None if items[item_key]["buy"] == 0 else items[item_key]["buy"],
                "sell_price": None if items[item_key]["sell"] == 0 else items[item_key]["sell"],
                "currency": items[item_key]["currency"],
            } for item_key in items.keys()]

        if len(symbols) == 0:
            return [item for item in data if item["symbol"] != "XAUUSD"]

        else:
            return [item for item in data if item["symbol"] in symbols]


    def get_multiple_ohlcv(self, symbols: List[str]):
        results = {}
        for sym in symbols:
            results[sym] = self.get_ohlcv_by_length(sym, length=30)
        return results
