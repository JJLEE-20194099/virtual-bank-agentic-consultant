import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
import requests

def match_sector(symbol):
    return company_data[symbol]["sector"]

df = pd.read_csv("/root/code/hackathon/virtual-bank-agentic-consultant/correct_trading_data.csv")

with open("/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/summary.json", "r", encoding="utf-8") as f:
    company_data = json.load(f)

df["sector"] = df["stock_code"].apply(match_sector)
with open("/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/customer/behaviour_labels.json", "r", encoding="utf-8") as f:
    trading_styles = json.load(f)

trading_style_df = pd.DataFrame()
trading_style_df["customer_id"] = trading_styles.keys()
trading_style_df["style"] = trading_styles.values()
df['datetime'] = pd.to_datetime(df['datetime'])
df['total_value'] = df['quantity'] * df['price']

customer_df = df.groupby('customer_id').agg(
    total_trades=('transaction_id', 'count'),
    total_volume=('quantity', 'sum'),
    total_invested=('total_value', 'sum'),
    total_fees=('fee', 'sum'),
    unique_stocks=('stock_code', 'nunique'),
    first_transaction=('datetime', 'min'),
    last_transaction=('datetime', 'max')
).reset_index()

customer_df["active_days"] = (
    (customer_df["last_transaction"] - customer_df["first_transaction"])
    .dt.days + 1
)

customer_df["trading_frequency"] = (
    customer_df["total_trades"] / customer_df["active_days"]
)

customer_df["total_invested_frequency"] = (
    customer_df["total_invested"] / customer_df["active_days"]
)

customer_df["total_volume_frequency"] = (
    customer_df["total_volume"] / customer_df["active_days"]
)


customer_df["total_fees_frequency"] = (
    customer_df["total_fees"] / customer_df["active_days"]
)

customer_df["unique_stocks_frequency"] = (
    customer_df["unique_stocks"] / customer_df["active_days"]
)


current_date = df['datetime'].max()
customer_df['recency'] = (current_date - customer_df['last_transaction']).dt.days

customer_df["active_days_recency"] = (
    customer_df["recency"] / customer_df["active_days"]
)

action_counts = df.pivot_table(index='customer_id', columns='action', values='transaction_id', aggfunc='count', fill_value=0)
customer_df['buy_ratio'] = list(action_counts['buy'] / (action_counts['buy'] + action_counts['sell']))
customer_df['buy_ratio'] = customer_df['buy_ratio'].fillna(0.5)

sector_pivot = df.pivot_table(index='customer_id', columns='sector', values='total_value', aggfunc='sum', fill_value=0)
sector_pct = sector_pivot.div(sector_pivot.sum(axis=1), axis=0)
sector_pct.columns = [f'pct_{col}' for col in sector_pct.columns]

final_df = pd.merge(customer_df, sector_pct, on='customer_id')

final_df = final_df.merge(trading_style_df, how='left', on = 'customer_id')
feature_df = final_df.drop(columns=["recency", 'active_days', 'total_trades', 'customer_id', 'first_transaction', 'last_transaction', 'style', "total_volume", "total_invested", "total_fees", "unique_stocks"])


cols_to_log = ['trading_frequency', 'total_volume_frequency', 'total_invested_frequency', 'total_fees_frequency']

for col in cols_to_log:
    feature_df[col] = np.log1p(feature_df[col])

train_features = list(feature_df.columns)

scaler = StandardScaler()
scaled_features = scaler.fit_transform(feature_df)


kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
final_df['cluster'] = kmeans.fit_predict(scaled_features)
joblib.dump(kmeans, "/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/checkpoints/stock_clustering_model.pkl")
joblib.dump(scaler, "/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/checkpoints/scaler.pkl")
loaded_model = joblib.load("/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/checkpoints/stock_clustering_model.pkl")
loaded_scaler = joblib.load("/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/checkpoints/scaler.pkl")

cluster_analysis = final_df.groupby('cluster').mean(numeric_only=True)


final_df['last_transaction'] = final_df['last_transaction'].dt.strftime("%Y-%m-%d %H:%M:%S")
final_df['first_transaction'] = final_df['first_transaction'].dt.strftime("%Y-%m-%d %H:%M:%S")

behaviour_data = final_df.to_dict(orient='records')
customer_ids = [item["customer_id"] for item in behaviour_data]
behaviour_data = dict(zip(customer_ids, behaviour_data))

centroids = loaded_model.cluster_centers_


BASE_URL = "http://localhost:8080/api/v1"

for customer_id in customer_ids:
    res = requests.post(
        f"{BASE_URL}/user/behaviour/create",
        json={
            "customer_id": customer_id,
            "behaviour_data": behaviour_data[customer_id]
        }
    )
