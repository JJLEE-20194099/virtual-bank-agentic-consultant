from feast import Entity, FeatureView, Field
from feast.types import Float32, Int64, String, Bool
from datetime import timedelta
from feast.infra.offline_stores.file_source import FileSource

user = Entity(
    name="user_id",
    join_keys=["user_id"]
)

user_feature_source = FileSource(
    path="data/user_features.parquet",
    timestamp_field="event_timestamp"
)

user_features_view = FeatureView(
    name="user_features",
    entities=[user],
    ttl=timedelta(days=90),
    schema=[
        Field(name="total_spend_3m", dtype=Float32),
        Field(name="avg_monthly_spend", dtype=Float32),
        Field(name="spend_std", dtype=Float32),
        Field(name="installment_ratio", dtype=Float32),
        Field(name="frequency_monthly", dtype=Float32),
        Field(name="travel_months", dtype=Int64),
        Field(name="weekend_spend_ratio", dtype=Float32),
        Field(name="top_category", dtype=String),
        Field(name="category_ratio_json", dtype=String),
        Field(name="trend_3m", dtype=String),
        Field(name="rent_detected", dtype=Bool),
        Field(name="high_value_ratio", dtype=Float32)
    ],
    online=True,
    source=user_feature_source
)