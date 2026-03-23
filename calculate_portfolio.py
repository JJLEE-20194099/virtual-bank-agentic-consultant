import pandas as pd 
import requests
import json
import os
import asyncpg
import asyncio
from backend.app.clients.db import PostgresClient
from backend.app.utils.portfolio import calculate_portfolio, stocks
from backend.app.clients.cache import RedisClient

db_client = PostgresClient(
    user="swin",
    password="swin",
    database="vbac",
    host="localhost"
)

redis_client = RedisClient()    
realtime_prices =  redis_client.get("realtime_prices:all")

async def save_portfolio():
    
    await db_client.connect()

    df = pd.read_csv("/root/code/hackathon/virtual-bank-agentic-consultant/correct_trading_data.csv")
    # df["datetime"] = pd.to_datetime(df["datetime"], format="mixed")
    
    user_ids = list(df.customer_id.unique())
    for user_id in user_ids:

        try:
            url = f"http://localhost:8080/api/v1/stock/{user_id}?limit=-1"
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()

                user_df = pd.DataFrame(data)
                print(user_id, len(user_df))
                user_df["datetime"] = pd.to_datetime(user_df["datetime"], format="mixed")
                # user_df = df[df.customer_id == user_id]
                user_df = user_df.sort_values("datetime").reset_index(drop=True)
                portfolio = calculate_portfolio(user_df, realtime_prices)

                await db_client.save_portfolio(user_id, portfolio)

                # res = requests.get(f"http://localhost:8080/api/v1/user/analyze/{user_id}")
                # if res.status_code == 200:
                #     portfolio_advice = res.json()
                #     await db_client.save_portfolio_advice(user_id, portfolio_advice)

        except Exception as e:
            print(e)


        

        




    await db_client.close()

if __name__ == "__main__":
    asyncio.run(save_portfolio())
