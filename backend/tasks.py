from celery_worker import celery_app
import asyncio

from app.clients.db import PostgresClient
from app.utils.portfolio import calculate_portfolio, fetch_realtime, stocks
import pandas as pd

db_client = PostgresClient(
    user="swin",
    password="swin",
    database="vbac",
    host="localhost"
)



async def _update_portfolio_async(user_id: str):

    realtime_prices = fetch_realtime(stocks)

    await db_client.connect()
    data = await db_client.get_stock_transactions_by_user(customer_id = user_id, limit=-1)
    user_df = pd.DataFrame(data)
    user_df["datetime"] = pd.to_datetime(user_df["datetime"], format="mixed")
    user_df = user_df.sort_values("datetime").reset_index(drop=True)
    portfolio = calculate_portfolio(user_df, realtime_prices)
    await db_client.save_portfolio(user_id, portfolio)

    await db_client.close()


@celery_app.task(name="tasks.update_portfolio")
def update_portfolio(user_id: str):
    asyncio.run(_update_portfolio_async(user_id))