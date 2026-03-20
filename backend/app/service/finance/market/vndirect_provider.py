import httpx
from dotenv import load_dotenv
from vnstock import Vnstock, Quote, Trading
import os
load_dotenv() 
import datetime

VNSTOCK_API_KEY = os.getenv("VNSTOCK_API_KEY")

# from vnstock import register_user
# register_user(api_key=VNSTOCK_API_KEY)

class VNDirectProvider:

    def get_ohlcv_by_length(self, symbol: str, length: int, interval: str):    

        stock = Quote(symbol=symbol, source='KBS')
        df = stock.history(length=length, interval=interval)
        df = df.sort_values(by="time", ascending=False)
        # df["time"] = df["time"].apply(lambda x: x.timestamp())

        data = df.to_dict(orient='records')

        return data

    def get_ohlcv(self, symbol, start_date, end_date, interval):

        stock = Vnstock().stock(symbol=symbol, source='KBS')

        print(start_date, end_date, interval)
        df = stock.quote.history(start=start_date, end=end_date, interval=interval)
        df = df.sort_values(by="time", ascending=False)
        # df["time"] = df["time"].apply(lambda x: x.timestamp())
        
        data = df.to_dict(orient='records')

        # item = data[0]
        # print("Date time:", datetime.datetime.fromtimestamp(item["time"]))
        # return {
        #     "symbol": symbol,
        #     "time": item["time"],
        #     "open": item["open"],
        #     "high": item["high"],
        #     "low": item["low"],
        #     "close": item["close"],
        #     "volume": item["volume"]
        # }

        return data

    def get_multiple(self, symbols: list[str] = ['VCB','ACB','TCB','BID']):
        board = Trading(source='KBS').price_board(symbols)

        data = board.to_dict(orient='records')
        
        return data