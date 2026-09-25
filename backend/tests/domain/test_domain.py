from datetime import datetime, timezone

import pytest

from domain.entities import (
    AnswerSnapshot,
    RecommendationRule,
    Specialist,
    StatusHistoryEntry,
    Ticket,
    new_id,
)
from domain.enums import TicketStatus, UrgencyLevel
from domain.exceptions import InvalidTicketTransitionError, OrganizationMismatchError
from domain.services import build_summary_text, compute_urgency, match_recommendation


def _ticket(**kwargs) -> Ticket:
    defaults = dict(
        id=new_id(),
        resident_ref="user-1",
        building_id="bld-1",
        address_snapshot="addr",
        organization_id="org-1",
        parent_category_id="p1",
        category_id="c1",
        answers_snapshot=[],
        recommendation_text_snapshot="rec",
        urgency_level=UrgencyLevel.MEDIUM,
        summary_text="sum",
        status=TicketStatus.NEW,
    )
    defaults.update(kwargs)
    return Ticket(**defaults)


def test_cancel_from_new_ok():
    t = _ticket(status=TicketStatus.NEW)
    t.cancel_by_resident("решилось само")
    assert t.status == TicketStatus.CANCELLED_BY_RESIDENT
    assert t.cancel_reason == "решилось само"


def test_cancel_from_accepted_ok():
    t = _ticket(status=TicketStatus.NEW)
    t.accept("disp-1")
    t.cancel_by_resident("ошибка")
    assert t.status == TicketStatus.CANCELLED_BY_RESIDENT


def test_cancel_from_in_progress_ok_with_reason():
    t = _ticket(status=TicketStatus.NEW)
    t.accept("disp-1")
    specialist = Specialist(
        id="s1", organization_id="org-1", full_name="A", skill_tags=[], active=True
    )
    t.assign_specialist(specialist)
    assert t.status == TicketStatus.IN_PROGRESS
    t.cancel_by_resident("мастер не нужен")
    assert t.status == TicketStatus.CANCELLED_BY_RESIDENT
    assert t.cancel_reason == "мастер не нужен"


def test_cancel_requires_reason():
    from domain.exceptions import ValidationError

    t = _ticket(status=TicketStatus.NEW)
    with pytest.raises(ValidationError):
        t.cancel_by_resident("   ")


def test_cancel_already_cancelled_raises():
    t = _ticket(status=TicketStatus.NEW)
    t.cancel_by_resident("один раз")
    with pytest.raises(InvalidTicketTransitionError):
        t.cancel_by_resident("ещё раз")


def test_assign_org_invariant():
    t = _ticket(status=TicketStatus.NEW, organization_id="org-1")
    t.accept("disp-1")
    foreign = Specialist(
        id="s2", organization_id="org-other", full_name="B", skill_tags=[], active=True
    )
    with pytest.raises(OrganizationMismatchError):
        t.assign_specialist(foreign)


def test_urgency_heuristic_cannot_shut_off():
    u = compute_urgency(UrgencyLevel.MEDIUM, None, ["cannot_shut_off=yes"])
    assert u == UrgencyLevel.HIGH


def test_urgency_heuristic_threat():
    u = compute_urgency(UrgencyLevel.LOW, None, ["threat_neighbors=yes"])
    assert u == UrgencyLevel.HIGH


def test_urgency_rule_sets_urgency():
    u = compute_urgency(UrgencyLevel.LOW, UrgencyLevel.HIGH, [])
    assert u == UrgencyLevel.HIGH


def test_urgency_door_open_night():
    u = compute_urgency(UrgencyLevel.LOW, None, ["door_open_night=yes"])
    assert u == UrgencyLevel.HIGH


def test_match_recommendation_priority():
    rules = [
        RecommendationRule(
            id="r1",
            category_id="c",
            match={"q1": "o1"},
            recommendation_text="low",
            priority=10,
            active=True,
        ),
        RecommendationRule(
            id="r2",
            category_id="c",
            match={"q1": "o1", "q2": "o2"},
            recommendation_text="high",
            priority=100,
            active=True,
        ),
    ]
    text, matched = match_recommendation(rules, {"q1": "o1", "q2": "o2"}, "default")
    assert text == "high"
    assert matched.id == "r2"


def test_match_recommendation_default():
    rules = [
        RecommendationRule(
            id="r1",
            category_id="c",
            match={"q1": "ox"},
            recommendation_text="nope",
            priority=100,
            active=True,
        )
    ]
    text, matched = match_recommendation(rules, {"q1": "o1"}, "default text")
    assert text == "default text"
    assert matched is None


def test_build_summary_text():
    answers = [
        AnswerSnapshot("q1", "Где?", "o1", "Пол/под сантехникой", "floor_plumbing"),
        AnswerSnapshot("q2", "Краны?", "o2", "Да, краны доступны", "can_shut_off"),
    ]
    s = build_summary_text("Протечка воды в квартире", answers, "Перекройте вентиль")
    assert "Протечка воды в квартире:" in s
    assert "Пол/под сантехникой" in s
    assert "Рекомендация: Перекройте вентиль" in s
