from __future__ import annotations

from typing import Optional

from domain.entities import AnswerSnapshot, RecommendationRule
from domain.enums import UrgencyLevel


def match_recommendation(
    rules: list[RecommendationRule],
    answers: dict[str, str],
    default_text: str,
) -> tuple[str, Optional[RecommendationRule]]:
    """
    Active rules sorted by priority desc; first where all match keys ⊆ answers.
    Returns (recommendation_text, matched_rule_or_None).
    """
    active = [r for r in rules if r.active]
    active.sort(key=lambda r: r.priority, reverse=True)
    for rule in active:
        if all(answers.get(qid) == oid for qid, oid in rule.match.items()):
            return rule.recommendation_text, rule
    return default_text, None


HIGH_URGENCY_CODES = frozenset(
    {
        "threat_neighbors=yes",
        "cannot_shut_off=yes",
        "door_open_night=yes",
    }
)


def compute_urgency(
    category_default: UrgencyLevel,
    matched_rule_sets_urgency: Optional[UrgencyLevel],
    answer_option_codes: list[str],
) -> UrgencyLevel:
    """
    Start with category default; if rule sets_urgency use it;
    else heuristic: threat_neighbors=yes, cannot_shut_off=yes, door_open_night=yes → at least HIGH.
    """
    urgency = category_default
    if matched_rule_sets_urgency is not None:
        urgency = matched_rule_sets_urgency
    else:
        if any(code in HIGH_URGENCY_CODES for code in answer_option_codes):
            urgency = UrgencyLevel.HIGH
    return urgency


def build_summary_text(
    category_name: str,
    answers: list[AnswerSnapshot],
    recommendation: str,
) -> str:
    """Human-readable Russian summary string."""
    parts = [f"{category_name}:"]
    answer_bits = []
    for a in answers:
        # Shorten common patterns for readability
        answer_bits.append(f"{a.option_label}")
    if answer_bits:
        parts.append("; ".join(answer_bits) + ".")
    parts.append(f"Рекомендация: {recommendation}")
    return " ".join(parts)
