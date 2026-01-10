class ComplianceIssue(dict):
    pass

def check_suitability(nlp, customer):
    issues = []

    if "INVESTMENT_DISCUSSION" in nlp["intents"]:
        if not customer.get("suitability_done"):
            issues.append(ComplianceIssue({
                "code": "MISSING_SUITABILITY",
                "severity": "HIGH",
                "regulation": "MiFID II Art. 25",
                "explanation": (
                    "Investment advice discussed before suitability "
                    "assessment was completed."
                )
            }))
    return issues


def check_disclosure(nlp, transcript):
    issues = []

    if "fee" not in transcript.lower():
        if "INVESTMENT_DISCUSSION" in nlp["intents"]:
            issues.append(ComplianceIssue({
                "code": "MISSING_FEE_DISCLOSURE",
                "severity": "MEDIUM",
                "regulation": "MiFID II Art. 24",
                "explanation": "Fees and costs were not disclosed."
            }))
    return issues