import asyncpg
import json
import asyncio

async def save_portfolio():
    conn = await asyncpg.connect(
        user="swin",
        password="swin",
        database='vbac',
        host='localhost'
    )

    await conn.close()

if __name__ == "__main__":
    asyncio.run(save_portfolio())
