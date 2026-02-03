def detect_behavior(features):
    patterns = []
    if features["travel_ratio"] > 0.4:
        patterns.append("travel-heavy")
    if features["installment_ratio"] > 0.5:
        patterns.append("high-installment")
    if features["trx_count"] > 80:
        behaviors.append("high-frequency-spender")
    print(features)
    return patterns