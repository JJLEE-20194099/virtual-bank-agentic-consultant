import httpx
from dotenv import load_dotenv
from vnstock import Vnstock
import os
load_dotenv() 
import datetime

VNSTOCK_API = os.getenv("VNSTOCK_API")

# from vnstock import register_user
# register_user(api_key=VNSTOCK_API)

class VNDirectProvider:


    def get_ohlcv(self, symbol, start_date, end_date, interval):

        stock = Vnstock().stock(symbol=symbol, source='KBS')

        print(start_date, end_date, interval)
        df = stock.quote.history(start=start_date, end=end_date, interval=interval)
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
