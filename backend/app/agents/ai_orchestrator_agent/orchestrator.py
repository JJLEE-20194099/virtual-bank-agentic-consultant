import json
from behavior_agent.behavior import detect_behavior
from explainable_agent.explain import explain
from product_rec_agent.recommend import recommend

FEATURE_STORE = "storage/feature_store.json"

def load_feature(user_id):
    with open(FEATURE_STORE) as f:
        store = json.load(f)
    return store[user_id]

def run_consultant(user_id):
    feature = load_feature(user_id)
    behaviors = detect_behavior(feature)
    insight = explain(feature, behaviors)
    product = recommend(behaviors)

    return {
        "behaviors": behaviors,
        "insight": insight,
        "recommendation": product
    }
