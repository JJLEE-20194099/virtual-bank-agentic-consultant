from app.clients.db import PostgresClient

db_client = PostgresClient(
    user="swin",
    password="swin",
    database="vbac",
    host="localhost"
)