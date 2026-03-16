"""Simple confidence scoring for advisory outputs.

This module is intentionally lightweight and deterministic for the PoC.
It provides a confidence score (0..1) and a boolean flag that can be used
by the “responsible AI / human review” gating logic.
"""

from typing import Optional


def score_confidence(
    feature: dict,
    intent_score: Optional[float] = None,
    is_transaction_trigger: bool = False,
) -> dict:
    """Return a dict containing confidence and whether the output needs human review.

    A simple rule-based scoring is used for the PoC. You can replace this with a
    proper ML-based calibration or a more complex heuristics engine later.
    """

    # Base confidence from feature completeness
    if not feature or feature.get("avg_monthly_spend") is None:
        base_confidence = 0.15
    else:
        # normalize avg_monthly_spend to a 0..1 scale for scoring purposes
        # this is intentionally coarse for the PoC.
        avg_spend = float(feature.get("avg_monthly_spend", 0))
        base_confidence = min(1.0, avg_spend / 100_000_000)

    # Intent classifier confidence helps determine whether the agent "understood" the question
    if intent_score is not None:
        base_confidence = min(base_confidence, float(intent_score))

    # Downgrade confidence if high-risk behavioral signals are present.
    # This simulates the “confidence gating” described in the proposal.
    if feature.get("high_value_ratio", 0) > 0.6 or feature.get("installment_ratio", 0) > 0.6:
        base_confidence = min(base_confidence, 0.65)

    # Transactions imply a stronger need for human review in this PoC.
    if is_transaction_trigger:
        base_confidence = min(base_confidence, 0.75)

    confidence = round(base_confidence, 2)

    return {
        "confidence": confidence,
        "requires_human_review": confidence < 0.7,
        "threshold": 0.7,
    }
