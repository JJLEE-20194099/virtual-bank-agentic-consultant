from app.service.recommendation.products import PRODUCTS

def recommend(nlp, compliance_issue, customer_data):
    if not compliance_issue["compliant"]:
        return None

    if "INVESTMENT_DISCUSSION" not in nlp["intents"]:
        return None

    recommendations = []
    for p in PRODUCTS:
        if p["risk"] == customer_data["risk_profile"]:
            recommendations.append({
                "product_id": p["id"],
                "name": p["name"],
                "confidence": 0.8
            })

    return recommendations
