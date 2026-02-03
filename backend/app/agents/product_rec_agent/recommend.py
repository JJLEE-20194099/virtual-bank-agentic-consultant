SERVICE_CATALOG = {
    "TRAVEL": [
        "Travel Credit Card",
        "Travel Insurance Package",
        "FX Rate Alert",
        "Airport Lounge Access"
    ],
    "FAMILY": [
        "Home Protection Insurance",
        "Health Insurance Package",
        "Education Savings Plan",
        "Family Budget Dashboard"
    ],
    "INSTALLMENT": [
        "Installment Optimization Service",
        "Debt Overview Dashboard",
        "Payment Reminder Service"
    ],
    "IMPULSE_CONTROL": [
        "Smart Spending Alert",
        "Monthly Budget Limit",
        "Cooling-off Notification"
    ],
    "WEALTH": [
        "Wealth Management Advisory",
        "Investment Portfolio Suggestion",
        "Priority Banking Service"
    ],
    "DIGITAL_ENGAGEMENT": [
        "Cashback Program",
        "Gamified Savings Challenge",
        "Personal Finance Insights"
    ],
    "BASIC": [
        "Basic Savings Account Upgrade",
        "Spending Summary Dashboard"
    ]
}

def recommend(behaviors: list[str]) -> list[str]:
    recommended = []
    applied_groups = set()

    if "travel-lover" in behaviors:
        recommended.extend(SERVICE_CATALOG["TRAVEL"])
        applied_groups.add("TRAVEL")

    if "family-settled" in behaviors:
        recommended.extend(SERVICE_CATALOG["FAMILY"])
        applied_groups.add("FAMILY")

    if "installment-dependent" in behaviors:
        recommended.extend(SERVICE_CATALOG["INSTALLMENT"])
        applied_groups.add("INSTALLMENT")

    if "impulsive-spender" in behaviors:
        recommended.extend(SERVICE_CATALOG["IMPULSE_CONTROL"])
        applied_groups.add("IMPULSE_CONTROL")

    if "big-spender" in behaviors and "stable-spending" in behaviors:
        recommended.extend(SERVICE_CATALOG["WEALTH"])
        applied_groups.add("WEALTH")

    if "high-engagement-user" in behaviors:
        recommended.extend(SERVICE_CATALOG["DIGITAL_ENGAGEMENT"])
        applied_groups.add("DIGITAL_ENGAGEMENT")

    if "budget-conscious" in behaviors:
                recommended.extend([
            "Spending Insights",
            "Monthly Expense Tracker",
            "Savings Goal Setup"
        ])

    if "spending-increasing" in behaviors:
        recommended.append("Spending Trend Alert")

    if "impulsive-spender" in behaviors:
        recommended = [
            s for s in recommended
            if "Credit Card" not in s
        ]

    if not recommended:
        recommended.extend(SERVICE_CATALOG["BASIC"])

    final_services = list(dict.fromkeys(recommended))

    return final_services[:6]
