from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from domain.enums import TicketStatus, UrgencyLevel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    dispatcher_id: str
    organization_id: str
    username: str
    full_name: str = ""


class BuildingOut(BaseModel):
    id: str
    addressLabel: str
    organizationId: str
    availableParentCategoryIds: Optional[list[str]] = None
    availableCategoryIds: Optional[list[str]] = None


class ParentCategoryIn(BaseModel):
    name: str
    order: int = 0
    active: bool = True
    defaultUrgencyHint: UrgencyLevel = UrgencyLevel.MEDIUM
    id: Optional[str] = None


class ParentCategoryOut(BaseModel):
    id: str
    name: str
    order: int
    active: bool
    defaultUrgencyHint: UrgencyLevel


class CategoryIn(BaseModel):
    parentCategoryId: str
    name: str
    order: int = 0
    active: bool = True
    defaultRecommendationText: str = ""
    defaultUrgency: UrgencyLevel = UrgencyLevel.MEDIUM
    organizationIds: Optional[list[str]] = None
    id: Optional[str] = None


class CategoryUpdateIn(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None
    order: Optional[int] = None
    defaultRecommendationText: Optional[str] = None
    defaultUrgency: Optional[UrgencyLevel] = None
    organizationIds: Optional[list[str]] = None


class CategoryOut(BaseModel):
    id: str
    parentCategoryId: str
    name: str
    active: bool
    order: int
    defaultRecommendationText: str
    defaultUrgency: UrgencyLevel
    organizationIds: Optional[list[str]] = None


class OptionIn(BaseModel):
    label: str
    code: str
    id: Optional[str] = None


class OptionOut(BaseModel):
    id: str
    label: str
    code: str


class QuestionIn(BaseModel):
    categoryId: str
    text: str
    order: int = 0
    active: bool = True
    options: list[OptionIn] = Field(default_factory=list)
    id: Optional[str] = None


class QuestionOut(BaseModel):
    id: str
    categoryId: str
    text: str
    order: int
    active: bool
    options: list[OptionOut]


class RuleIn(BaseModel):
    categoryId: str
    match: dict[str, str]
    recommendationText: str
    priority: int
    active: bool = True
    setsUrgency: Optional[UrgencyLevel] = None
    id: Optional[str] = None


class RuleOut(BaseModel):
    id: str
    categoryId: str
    match: dict[str, str]
    recommendationText: str
    priority: int
    active: bool
    setsUrgency: Optional[UrgencyLevel] = None


class CategoryTreeNode(BaseModel):
    parent: ParentCategoryOut
    categories: list[CategoryOut]


class BuildingCategoriesOut(BaseModel):
    building: BuildingOut
    tree: list[CategoryTreeNode]


class QuestionnaireOut(BaseModel):
    category: CategoryOut
    parent: Optional[ParentCategoryOut] = None
    questions: list[QuestionOut]
    rules: list[RuleOut]


class SubmitTicketIn(BaseModel):
    buildingId: str
    categoryId: str
    answers: dict[str, str]
    photoUrl: Optional[str] = None


class AnswerSnapshotOut(BaseModel):
    questionId: str
    questionLabel: str
    optionId: str
    optionLabel: str
    optionCode: str


class StatusHistoryOut(BaseModel):
    status: TicketStatus
    at: datetime
    note: Optional[str] = None


class TicketOut(BaseModel):
    id: str
    residentRef: str
    buildingId: str
    addressSnapshot: str
    organizationId: str
    parentCategoryId: str
    categoryId: str
    answersSnapshot: list[AnswerSnapshotOut]
    recommendationTextSnapshot: str
    urgencyLevel: UrgencyLevel
    summaryText: str
    status: TicketStatus
    photoUrl: Optional[str] = None
    assigneeSpecialistId: Optional[str] = None
    takenByDispatcherId: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    statusHistory: list[StatusHistoryOut]


class AssignIn(BaseModel):
    specialistId: str


class SpecialistIn(BaseModel):
    organizationId: str
    fullName: str
    skillTags: list[str] = Field(default_factory=list)
    active: bool = True
    id: Optional[str] = None


class SpecialistUpdateIn(BaseModel):
    fullName: Optional[str] = None
    skillTags: Optional[list[str]] = None
    active: Optional[bool] = None


class SpecialistOut(BaseModel):
    id: str
    organizationId: str
    fullName: str
    skillTags: list[str]
    active: bool


class WebhookIn(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


# --- mappers ---


def building_out(b) -> BuildingOut:
    return BuildingOut(
        id=b.id,
        addressLabel=b.address_label,
        organizationId=b.organization_id,
        availableParentCategoryIds=b.available_parent_category_ids,
        availableCategoryIds=b.available_category_ids,
    )


def parent_out(p) -> ParentCategoryOut:
    return ParentCategoryOut(
        id=p.id,
        name=p.name,
        order=p.order,
        active=p.active,
        defaultUrgencyHint=p.default_urgency_hint,
    )


def category_out(c) -> CategoryOut:
    return CategoryOut(
        id=c.id,
        parentCategoryId=c.parent_category_id,
        name=c.name,
        active=c.active,
        order=c.order,
        defaultRecommendationText=c.default_recommendation_text,
        defaultUrgency=c.default_urgency,
        organizationIds=c.organization_ids,
    )


def question_out(q) -> QuestionOut:
    return QuestionOut(
        id=q.id,
        categoryId=q.category_id,
        text=q.text,
        order=q.order,
        active=q.active,
        options=[OptionOut(id=o.id, label=o.label, code=o.code) for o in q.options],
    )


def rule_out(r) -> RuleOut:
    return RuleOut(
        id=r.id,
        categoryId=r.category_id,
        match=r.match,
        recommendationText=r.recommendation_text,
        priority=r.priority,
        active=r.active,
        setsUrgency=r.sets_urgency,
    )


def specialist_out(s) -> SpecialistOut:
    return SpecialistOut(
        id=s.id,
        organizationId=s.organization_id,
        fullName=s.full_name,
        skillTags=s.skill_tags,
        active=s.active,
    )


def ticket_out(t) -> TicketOut:
    return TicketOut(
        id=t.id,
        residentRef=t.resident_ref,
        buildingId=t.building_id,
        addressSnapshot=t.address_snapshot,
        organizationId=t.organization_id,
        parentCategoryId=t.parent_category_id,
        categoryId=t.category_id,
        answersSnapshot=[
            AnswerSnapshotOut(
                questionId=a.question_id,
                questionLabel=a.question_label,
                optionId=a.option_id,
                optionLabel=a.option_label,
                optionCode=a.option_code,
            )
            for a in t.answers_snapshot
        ],
        recommendationTextSnapshot=t.recommendation_text_snapshot,
        urgencyLevel=t.urgency_level,
        summaryText=t.summary_text,
        status=t.status,
        photoUrl=t.photo_url,
        assigneeSpecialistId=t.assignee_specialist_id,
        takenByDispatcherId=t.taken_by_dispatcher_id,
        createdAt=t.created_at,
        updatedAt=t.updated_at,
        statusHistory=[
            StatusHistoryOut(status=h.status, at=h.at, note=h.note) for h in t.status_history
        ],
    )
