import asyncpg
import json
from typing import Any, Dict, Optional, List


class PostgresClient:
    def __init__(self, user: str, password: str, database: str, host: str = "localhost", port: int = 5432):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.conn: Optional[asyncpg.Connection] = None

    async def connect(self):
        self.conn = await asyncpg.connect(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
            port=self.port
        )

    def _normalize(self, record):
        from decimal import Decimal
        return {
            k: float(v) if isinstance(v, Decimal) else v
            for k, v in record.items()
        }

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def init_stock_user_behaviour_table(self):
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_user_behaviour (
            id SERIAL PRIMARY KEY,
            user_id TEXT PRIMARY KEY,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    async def save_stock_user_behaviour(self, user_id: str, behaviour_data):
        await self.conn.execute("""
            INSERT INTO stock_user_behaviour(user_id, data)
            VALUES($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET data = EXCLUDED.data,
                          created_at = CURRENT_TIMESTAMP
        """,
        user_id,
        json.dumps(behaviour_data)   
    )

    async def get_stock_user_behaviour(self, user_id: str) -> Optional[Dict]:
        row = await self.conn.fetchrow("""
            SELECT data
            FROM stock_user_behaviour
            WHERE user_id = $1
        """, user_id)

        return json.loads(row["data"]) if row else None
    
    async def delete_stock_user_behaviour(self, user_id: str):
        await self.conn.execute("""
            DELETE FROM stock_user_behaviour
            WHERE user_id = $1
        """, user_id)

    async def delete_stock_user_behaviour_table(self):
        await self.conn.execute("""
            TRUNCATE TABLE stock_user_behaviour;
        """)

    async def init_user_table(self):
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    async def init_stock_product_recommendation_table(self):
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_product_recommendation (
            user_id TEXT PRIMARY KEY,
            data JSONB NOT NULL,
            status TEXT CHECK (status IN ('pending', 'processing', 'done', 'failed')) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    async def get_stock_product_recommendation(self, user_id: str) -> Optional[Dict]:
        row = await self.conn.fetchrow("""
            SELECT *
            FROM stock_product_recommendation
            WHERE user_id = $1
        """, user_id)

        row = dict(row) 

        row["data"] = json.loads(row["data"])

        return row

    async def insert_stock_product_recommendation(self, user_id: str, data: Dict[str, Any], status:str):
        await self.conn.execute("""
            INSERT INTO stock_product_recommendation(user_id, data, status)
            VALUES($1, $2, $3)
            ON CONFLICT (user_id)
            DO UPDATE SET data = EXCLUDED.data,
                          created_at = CURRENT_TIMESTAMP
        """,
        user_id,
        json.dumps(data),
        status
        )


    async def get_user(self, user_id: str) -> Optional[Dict]:
        row = await self.conn.fetchrow("""
            SELECT data
            FROM users
            WHERE user_id = $1
        """, user_id)

        return json.loads(row["data"]) if row else None
    

    async def delete_user_table(self):
        await self.conn.execute("""
            TRUNCATE TABLE users;
        """)

    async def insert_user(self, user_id: str, data: Dict[str, Any]):
        await self.conn.execute("""
            INSERT INTO users(user_id, data)
            VALUES($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET data = EXCLUDED.data,
                          created_at = CURRENT_TIMESTAMP
        """,
        user_id,
        json.dumps(data)   
        )
        

    async def init_portfolio_table(self):
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_summary (
            user_id TEXT PRIMARY KEY,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    

    async def delete_portfolio_table(self):
        await self.conn.execute("""
            TRUNCATE TABLE portfolio_summary;
        """)


        

    async def save_portfolio(self, user_id: str, portfolio: Dict[str, Any]):
        await self.conn.execute("""
            INSERT INTO portfolio_summary(user_id, data)
            VALUES($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET data = EXCLUDED.data,
                          created_at = CURRENT_TIMESTAMP
        """,
        user_id,
        json.dumps(portfolio)   
    )

    


    async def get_portfolio(self, user_id: str) -> Optional[Dict]:
        row = await self.conn.fetchrow("""
            SELECT data
            FROM portfolio_summary
            WHERE user_id = $1
        """, user_id)

        return json.loads(row["data"]) if row else None


    async def delete_portfolio(self, user_id: str):
        await self.conn.execute("""
            DELETE FROM portfolio_summary
            WHERE user_id = $1
        """, user_id)

    

    async def init_stock_summary_table(self):
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_summary (
            symbol TEXT PRIMARY KEY,
            company TEXT NOT NULL,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    async def save_stock_summary(self, symbol: str, stock_summary: Dict[str, Any]):
        await self.conn.execute("""
            INSERT INTO stock_summary(symbol, company, data)
            VALUES($1, $2, $3)
            ON CONFLICT (symbol)
            DO UPDATE SET data = EXCLUDED.data,
                          created_at = CURRENT_TIMESTAMP
        """,
        symbol,
        symbol,
        json.dumps(stock_summary)   
    )


    async def get_stock_summary(self, symbol: str) -> Optional[Dict]:
        row = await self.conn.fetchrow("""
            SELECT *
            FROM stock_summary
            WHERE symbol = $1
        """, symbol)

        row["data"] = json.loads(row["data"])
        return row



    async def get_stock_summary_by_symbols(self, symbols: List[str]):
        rows = await self.conn.fetch("""
            SELECT *
            FROM stock_summary
            WHERE symbol = ANY($1)
        """, symbols)

        return [{**item, "data": json.loads(item["data"])} for item in rows]



    async def delete_stock_summary(self, symbol: str):
        await self.conn.execute("""
            DELETE FROM stock_summary
            WHERE symbol = $1
        """, symbol)


    async def init_stock_transactions_table(self):
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_transaction 
        (
            id SERIAL PRIMARY KEY,
            transaction_id TEXT UNIQUE,
            customer_id TEXT NOT NULL,

            datetime TIMESTAMP NOT NULL,
            stock_code TEXT NOT NULL,

            action TEXT CHECK (action IN ('buy', 'sell')),

            quantity INT NOT NULL,
            price NUMERIC NOT NULL,
            fee NUMERIC NOT NULL
        );
        """)

        await self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_customer_time
        ON stock_transaction(customer_id, datetime);
        """)
    
        await self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_stock
        ON stock_transaction(stock_code);
        """)

        await self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_user_stock
        ON stock_transaction(customer_id, stock_code);
        """)

    async def get_all_customer_ids(self):
        rows = await self.conn.fetch("""
            SELECT DISTINCT customer_id FROM stock_transaction;
        """)
        return [row["customer_id"] for row in rows]

    async def insert_stock_transactions(self, transactions: List):
        await self.conn.executemany("""
            INSERT INTO stock_transaction(
                transaction_id,
                customer_id,
                datetime,
                stock_code,
                action,
                quantity,
                price,
                fee
            )
            VALUES($1,$2,$3,$4,$5,$6,$7,$8)
            ON CONFLICT (transaction_id) DO NOTHING
        """, [
            (
                t["transaction_id"],
                t["customer_id"],
                t["datetime"],
                t["stock_code"],
                t["action"],
                t["quantity"],
                t["price"],
                t["fee"]
            )
            for t in transactions
        ])

    async def get_stock_transactions_by_user(self, customer_id: str, limit: int = 20, offset: int = 0):

        query = """
            SELECT *
            FROM stock_transaction
            WHERE customer_id = $1
            ORDER BY datetime DESC
        """

        params = [customer_id]
        if limit != -1:
            query += " LIMIT $2 OFFSET $3"
            params.extend([limit, offset])

        
            rows = await self.conn.fetch(query, *params)
        else:
            rows = await self.conn.fetch(query, customer_id)


        return [self._normalize(dict(r)) for r in rows]

    async def get_stock_transactions_by_user_and_stock(self, customer_id: str, stock_code: str, limit: int = 20, offset: int = 0):

        query = """
            SELECT *
            FROM stock_transaction
            WHERE customer_id = $1 AND stock_code = $2
            ORDER BY datetime DESC
        """

        params = [customer_id, stock_code]
        if limit != -1:
            query += " LIMIT $3 OFFSET $4"
            params.extend([limit, offset])

            rows = await self.conn.fetch(query, *params)
        else:
            rows = await self.conn.fetch(query, customer_id, stock_code)



        return [self._normalize(dict(r)) for r in rows]


    async def delete_stock_transaction(self, transaction_id: str):
        await self.conn.execute("""
            DELETE FROM stock_transaction
            WHERE transaction_id = $1
        """, transaction_id)

    
    async def init_portfolio_advice_table(self):
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_advice (
            user_id TEXT PRIMARY KEY,
            data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    async def save_portfolio_advice(self, user_id: str, portfolio_advice):
        await self.conn.execute("""
            INSERT INTO portfolio_advice(user_id, data)
            VALUES($1, $2)
            ON CONFLICT (user_id)
            DO UPDATE SET data = EXCLUDED.data,
                          created_at = CURRENT_TIMESTAMP
        """,
        user_id,
        json.dumps(portfolio_advice)   
    )

    async def get_portfolio_advice(self, user_id: str) -> Optional[Dict]:
        row = await self.conn.fetchrow("""
            SELECT data
            FROM portfolio_advice
            WHERE user_id = $1
        """, user_id)

        return json.loads(row["data"]) if row else None