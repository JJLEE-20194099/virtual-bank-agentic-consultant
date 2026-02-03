import json
from app.agents.behavior_agent.predict import detect_behavior
from app.agents.explainable_agent.explain import explain
from app.agents.product_rec_agent.recommend import recommend

FEATURE_STORE = "app/storage/feature_store.json"

def load_feature(user_id):
    with open(FEATURE_STORE) as f:
        store = json.load(f)
    return store[user_id]

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
