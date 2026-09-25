from __future__ import annotations

from datetime import datetime
from typing import Optional

from domain.entities import (
    AnswerSnapshot,
    Building,
    Category,
    DispatcherAccount,
    Option,
    Organization,
    ParentCategory,
    Question,
    RecommendationRule,
    Specialist,
    StatusHistoryEntry,
    Ticket,
)
from domain.enums import TicketStatus, UrgencyLevel
from infrastructure.persistence.models import (
    BuildingModel,
    CategoryModel,
    DispatcherModel,
    OrganizationModel,
    ParentCategoryModel,
    QuestionModel,
    RecommendationRuleModel,
    SpecialistModel,
    TicketModel,
)


def org_to_domain(m: OrganizationModel) -> Organization:
    return Organization(id=m.id, name=m.name)


def dispatcher_to_domain(m: DispatcherModel) -> DispatcherAccount:
    return DispatcherAccount(
        id=m.id,
        username=m.username,
        password_hash=m.password_hash,
        organization_id=m.organization_id,
        full_name=m.full_name or "",
    )


def specialist_to_domain(m: SpecialistModel) -> Specialist:
    return Specialist(
        id=m.id,
        organization_id=m.organization_id,
        full_name=m.full_name,
        skill_tags=list(m.skill_tags or []),
        active=m.active,
    )


def building_to_domain(m: BuildingModel) -> Building:
    return Building(
        id=m.id,
        address_label=m.address_label,
        organization_id=m.organization_id,
        available_parent_category_ids=m.available_parent_category_ids,
        available_category_ids=m.available_category_ids,
    )


def parent_to_domain(m: ParentCategoryModel) -> ParentCategory:
    return ParentCategory(
        id=m.id,
        name=m.name,
        order=m.order,
        active=m.active,
        default_urgency_hint=UrgencyLevel(m.default_urgency_hint),
    )


def category_to_domain(m: CategoryModel) -> Category:
    return Category(
        id=m.id,
        parent_category_id=m.parent_category_id,
        name=m.name,
        active=m.active,
        order=m.order,
        default_recommendation_text=m.default_recommendation_text or "",
        default_urgency=UrgencyLevel(m.default_urgency),
        organization_ids=m.organization_ids,
    )


def question_to_domain(m: QuestionModel) -> Question:
    options = [
        Option(id=o["id"], label=o["label"], code=o["code"]) for o in (m.options or [])
    ]
    return Question(
        id=m.id,
        category_id=m.category_id,
        text=m.text,
        order=m.order,
        active=m.active,
        options=options,
    )


def rule_to_domain(m: RecommendationRuleModel) -> RecommendationRule:
    return RecommendationRule(
        id=m.id,
        category_id=m.category_id,
        match=dict(m.match or {}),
        recommendation_text=m.recommendation_text,
        priority=m.priority,
        active=m.active,
        sets_urgency=UrgencyLevel(m.sets_urgency) if m.sets_urgency else None,
    )


def _parse_dt(value) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def ticket_to_domain(m: TicketModel) -> Ticket:
    answers = [
        AnswerSnapshot(
            question_id=a["question_id"],
            question_label=a["question_label"],
            option_id=a["option_id"],
            option_label=a["option_label"],
            option_code=a["option_code"],
        )
        for a in (m.answers_snapshot or [])
    ]
    history = [
        StatusHistoryEntry(
            status=TicketStatus(h["status"]),
            at=_parse_dt(h["at"]),
            note=h.get("note"),
        )
        for h in (m.status_history or [])
    ]
    return Ticket(
        id=m.id,
        resident_ref=m.resident_ref,
        building_id=m.building_id,
        address_snapshot=m.address_snapshot,
        organization_id=m.organization_id,
        parent_category_id=m.parent_category_id,
        category_id=m.category_id,
        answers_snapshot=answers,
        recommendation_text_snapshot=m.recommendation_text_snapshot or "",
        urgency_level=UrgencyLevel(m.urgency_level),
        summary_text=m.summary_text or "",
        status=TicketStatus(m.status),
        photo_url=m.photo_url,
        assignee_specialist_id=m.assignee_specialist_id,
        taken_by_dispatcher_id=m.taken_by_dispatcher_id,
        created_at=m.created_at,
        updated_at=m.updated_at,
        status_history=history,
    )


def ticket_to_model_fields(t: Ticket) -> dict:
    return {
        "id": t.id,
        "resident_ref": t.resident_ref,
        "building_id": t.building_id,
        "address_snapshot": t.address_snapshot,
        "organization_id": t.organization_id,
        "parent_category_id": t.parent_category_id,
        "category_id": t.category_id,
        "answers_snapshot": [
            {
                "question_id": a.question_id,
                "question_label": a.question_label,
                "option_id": a.option_id,
                "option_label": a.option_label,
                "option_code": a.option_code,
            }
            for a in t.answers_snapshot
        ],
        "recommendation_text_snapshot": t.recommendation_text_snapshot,
        "urgency_level": t.urgency_level.value,
        "summary_text": t.summary_text,
        "status": t.status.value,
        "photo_url": t.photo_url,
        "assignee_specialist_id": t.assignee_specialist_id,
        "taken_by_dispatcher_id": t.taken_by_dispatcher_id,
        "created_at": t.created_at,
        "updated_at": t.updated_at,
        "status_history": [
            {
                "status": h.status.value,
                "at": h.at.isoformat() if isinstance(h.at, datetime) else h.at,
                "note": h.note,
            }
            for h in t.status_history
        ],
    }
