import pandas as pd

from app.core.model_instance import model_client

def make_cluster_features(test_df):

    cols_to_log = ['trading_frequency', 'total_volume_frequency', 'total_invested_frequency', 'total_fees_frequency']
    train_features = ['trading_frequency',
        'total_invested_frequency',
        'total_volume_frequency',
        'total_fees_frequency',
        'unique_stocks_frequency',
        'active_days_recency',
        'buy_ratio',
        'pct_Banking',
        'pct_Basic Materials',
        'pct_Communication Services',
        'pct_Conglomerates',
        'pct_Consumer Discretionary',
        'pct_Consumer Staples',
        'pct_Energy',
        'pct_Financial Services',
        'pct_Industrials',
        'pct_Insurance',
        'pct_Real Estate',
        'pct_Retail',
        'pct_Technology',
        'pct_Utilities']
    test_df['datetime'] = pd.to_datetime(test_df['datetime'])
    test_df['total_value'] = test_df['quantity'] * test_df['price']

    customer_test_df = test_df.groupby('customer_id').agg(
        total_trades=('transaction_id', 'count'),
        total_volume=('quantity', 'sum'),
        total_invested=('total_value', 'sum'),
        total_fees=('fee', 'sum'),
        unique_stocks=('stock_code', 'nunique'),
        first_transaction=('datetime', 'min'),
        last_transaction=('datetime', 'max')
    ).reset_index()
    current_date = test_df['datetime'].max()
    customer_test_df['recency'] = (current_date - customer_test_df['last_transaction']).dt.days

    customer_test_df["active_days"] = (
        (customer_test_df["last_transaction"] - customer_test_df["first_transaction"])
        .dt.days + 1
    )

    customer_test_df["trading_frequency"] = (
        customer_test_df["total_trades"] / customer_test_df["active_days"]
    )

    customer_test_df["total_invested_frequency"] = (
        customer_test_df["total_invested"] / customer_test_df["active_days"]
    )

    customer_test_df["total_volume_frequency"] = (
        customer_test_df["total_volume"] / customer_test_df["active_days"]
    )


    customer_test_df["total_fees_frequency"] = (
        customer_test_df["total_fees"] / customer_test_df["active_days"]
    )

    customer_test_df["unique_stocks_frequency"] = (
        customer_test_df["unique_stocks"] / customer_test_df["active_days"]
    )


    customer_test_df["active_days_recency"] = (
        customer_test_df["recency"] / customer_test_df["active_days"]
    )

    action_counts = test_df.pivot_table(index='customer_id', columns='action', values='transaction_id', aggfunc='count', fill_value=0)
    action_counts = action_counts.reindex(columns=["buy", "sell"], fill_value=0)
    customer_test_df['buy_ratio'] = list(action_counts['buy'] / (action_counts['buy'] + action_counts['sell']))
    customer_test_df['buy_ratio'] = customer_test_df['buy_ratio'].fillna(0.5)
    test_sector_pivot = test_df.pivot_table(index='customer_id', columns='sector', values='total_value', aggfunc='sum', fill_value=0)

    test_sector_pct = test_sector_pivot.div(test_sector_pivot.sum(axis=1), axis=0)
    test_sector_pct.columns = [f'pct_{col}' for col in test_sector_pct.columns]

    test_final_df = pd.merge(customer_test_df, test_sector_pct, on='customer_id')
    test_feature_df = test_final_df.drop(columns=["recency", 'active_days', 'total_trades', 'customer_id', 'first_transaction', 'last_transaction', "total_volume", "total_invested", "total_fees", "unique_stocks"])

    for col in cols_to_log:
        test_feature_df[col] = np.log1p(test_feature_df[col])

    missing_test_features = set(train_features) - set(test_feature_df.columns)
    for col in missing_test_features:
        test_feature_df[col] = 0 
    test_feature_df =  test_feature_df[train_features]

    scaled_test_features = model_client.loaded_scaler.transform(test_feature_df)

    test_final_df['last_transaction'] = test_final_df['last_transaction'].dt.strftime("%Y-%m-%d %H:%M:%S")
    test_final_df['first_transaction'] = test_final_df['first_transaction'].dt.strftime("%Y-%m-%d %H:%M:%S")

    behaviour_feature_data = test_final_df.to_dict(orient='records')

    return scaled_test_features, behaviour_feature_data

    
