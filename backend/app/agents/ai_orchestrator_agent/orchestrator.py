import json
from app.agents.behavior_agent.predict import detect_behavior
from app.agents.explainable_agent.explain import explain
from app.agents.product_rec_agent.recommend import recommend

from feast import FeatureStore

store = FeatureStore(
    repo_path="app/service/feature_engine/feature_store/repo"
)

FEATURE_LIST = [
    "user_features:total_spend_3m",
    "user_features:avg_monthly_spend",
    "user_features:spend_std",
    "user_features:installment_ratio",
    "user_features:frequency_monthly",
    "user_features:travel_months",
    "user_features:weekend_spend_ratio",
    "user_features:top_category",
    "user_features:trend_3m",
    "user_features:category_ratio_json",
    "user_features:rent_detected",
    "user_features:high_value_ratio"
]

def load_feature(user_id):
    feature_vector = store.get_online_features(
        features=FEATURE_LIST,
        entity_rows=[{"user_id": user_id}]
    ).to_dict()
    print(feature_vector)
    feature_vector["category_ratio"] = [json.loads(feature_vector["category_ratio_json"][0])]
    del feature_vector["category_ratio_json"]

    return {k: v[0] for k, v in feature_vector.items()}

def run_consultant(user_id):
    feature = load_feature(user_id)
    behaviors = detect_behavior(feature)
    product = recommend(behaviors)
    insight = explain(feature, behaviors, product)

    return {
        "feature": feature,
        "behaviors": behaviors,
        "insight": insight,
        "recommendation": product
    }
