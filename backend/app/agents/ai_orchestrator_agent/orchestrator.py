import json
from typing import Optional

from app.agents.behavior_agent.predict import detect_behavior
from app.agents.confidence_agent import score_confidence
from app.agents.explainable_agent.explain import explain
from app.agents.product_rec_agent.recommend import recommend
from app.agents.sale_agent import SaleAgent

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


def load_feature(user_id: str) -> dict:
    feature_vector = store.get_online_features(
        features=FEATURE_LIST,
        entity_rows=[{"user_id": user_id}]
    ).to_dict()
    feature_vector["category_ratio"] = [json.loads(feature_vector["category_ratio_json"][0])]
    del feature_vector["category_ratio_json"]

    return {k: v[0] for k, v in feature_vector.items()}


def run_consultant(
    user_id: str,
    query: Optional[str] = None,
    intent_score: Optional[float] = None,
    is_transaction_trigger: bool = False,
):
    """Run the core advisory flow.

    This function is used for both transaction-triggered and chat-triggered advisory flows.
    """

    feature = load_feature(user_id)
    behaviors = detect_behavior(feature)
    product_recs = recommend(behaviors)

    chat_reply = None
    if query:
        chat_reply = SaleAgent().run(
            customer_data={},
            query=query,
            qa_data={},
            bank_services={},
        )

    insight = explain(feature, behaviors, product_recs)
    confidence = score_confidence(
        feature,
        intent_score=intent_score,
        is_transaction_trigger=is_transaction_trigger,
    )

    return {
        "feature": feature,
        "behaviors": behaviors,
        "recommendation": product_recs,
        "explanation": insight,
        "confidence": confidence,
        "chat_reply": chat_reply,
    }
