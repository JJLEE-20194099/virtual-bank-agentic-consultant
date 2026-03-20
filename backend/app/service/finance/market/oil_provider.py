import httpx
import datetime
from typing import List, Optional
from dotenv import load_dotenv
import os
load_dotenv() 
from bs4 import BeautifulSoup

OIL_API_KEY = os.getenv("OIL_API_KEY")

BASE_URL = "https://api.oilpriceapi.com/v1"

DOMESTIC_BASE_URL = "https://www.pvoil.com.vn/api/oilprice/load-view"

class OilProvider:

    def __init__(self):
        self.client = httpx.Client(timeout=10)
        self.headers = {
            "Authorization": f"Token {OIL_API_KEY}",
            "Content-Type": "application/json"
        }
        self.symbol = "BRENT_CRUDE_USD"
        self.products = ["Xăng RON 95-III", "Xăng E5 RON 92-II", "Dầu DO 0,05S-II", "Dầu KO"]


    def get_ohlcv_by_length(self, length: int = 30):
        url = f"{BASE_URL}/prices/historical"
        params = {
            "by_code": self.symbol,
            "interval": "daily",
            "limit": length
        }
        resp = self.client.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        items = resp.json()["data"]["prices"]
        ohlcv_list = []
        for item in items:
            ohlcv_list.append({
                "time": item["created_at"],
                "close": item["price"]
            })
        return ohlcv_list

    def get_latest(self):
        url = f"{BASE_URL}/prices/latest"
        params = {
            "by_code": self.symbol
        }
        resp = self.client.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        item = resp.json()["data"]

        data = {
            "symbol": self.symbol,
            "provider": "Brent Crude Oil",
            "sell_price": item.get("price"),
            "time": item["updated_at"],
            "currency": "USD"
        }
        return data

    def parse_html_prices(self, html_text: str, date: str):
        soup = BeautifulSoup(html_text, "html.parser")
        table = soup.find("table")
        rows = table.tbody.find_all("tr")
        result = []

        for row in rows:
            cols = row.find_all("td")
            product_name = cols[1].get_text(strip=True)
            if product_name not in self.products:
                continue
            price_text = cols[2].get_text(strip=True).replace("đ", "").replace(".", "")
            price = float(price_text)
            result.append({
                "product": product_name,
                "sell_price": price,
                "currency": "VND",
                "time": date
            })
        return result

    def get_domestic_latest(self, max_days_back: int = 7):
        for i in range(max_days_back):
            day = datetime.datetime.now() - datetime.timedelta(days=i)
            date_str = day.strftime("%d/%m/%Y")
            params = {"date": date_str}
            resp = self.client.get(DOMESTIC_BASE_URL, params=params)
            resp.raise_for_status()
            prices = self.parse_html_prices(resp.text, datetime.datetime.now().strftime("%Y-%m-%d"))
            if prices:  
                return prices
       
        return []

    def get_domestic_ohlcv_by_length(self, symbol, length, max_days_back:int = 7):
        data = []
        i = 0
        while i < length:
            found = False
            for back in range(max_days_back):
                day = datetime.datetime.now() - datetime.timedelta(days=i + back)
                date_str = day.strftime("%d/%m/%Y")
                params = {"date": date_str}
                resp = self.client.get(DOMESTIC_BASE_URL, params=params)
                resp.raise_for_status()
                prices = self.parse_html_prices(resp.text, day.strftime("%Y-%m-%d"))
                for price in prices:
                    if price["product"] == symbol:
                        data.append(price)
                        found = True
                        break
                if found:
                    i = i + back
                    break
            
            i = i + 1
                    
        return data        

    


    
