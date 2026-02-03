def detect_behavior(f: dict):
    behaviors = []

    if f["avg_monthly_spend"] > 30_000_000:
        behaviors.append("big-spender")
    else:
        behaviors.append("budget-conscious")

    if f["spend_std"] < 0.2 * f["avg_monthly_spend"]:
        behaviors.append("stable-spending")

    if f["trend_3m"] == "increasing":
        behaviors.append("spending-increasing")

    if f["category_ratio"].get("travel", 0) > 0.35:
        behaviors.append("travel-lover")

    if f["rent_detected"]:
        behaviors.append("family-settled")

    if f["installment_ratio"] > 0.5:
        behaviors.append("installment-dependent")

    if f["high_value_ratio"] > 0.3:
        behaviors.append("impulsive-spender")

    if f["frequency_monthly"] > 70:
        behaviors.append("high-engagement-user")

    return behaviors
