from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from domain.enums import TicketStatus, UrgencyLevel
from domain.exceptions import InvalidTicketTransitionError, OrganizationMismatchError


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


@dataclass
class Organization:
    id: str
    name: str


@dataclass
class Specialist:
    id: str
    organization_id: str
    full_name: str
    skill_tags: list[str] = field(default_factory=list)
    active: bool = True


@dataclass
class Building:
    id: str
    address_label: str
    organization_id: str
    available_parent_category_ids: Optional[list[str]] = None
    available_category_ids: Optional[list[str]] = None


@dataclass
class ParentCategory:
    id: str
    name: str
    order: int
    active: bool = True
    default_urgency_hint: UrgencyLevel = UrgencyLevel.MEDIUM


@dataclass
class Category:
    id: str
    parent_category_id: str
    name: str
    active: bool = True
    order: int = 0
    default_recommendation_text: str = ""
    default_urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    organization_ids: Optional[list[str]] = None


@dataclass
class Option:
    id: str
    label: str
    code: str


@dataclass
class Question:
    id: str
    category_id: str
    text: str
    order: int
    active: bool = True
    options: list[Option] = field(default_factory=list)


@dataclass
class RecommendationRule:
    id: str
    category_id: str
    match: dict[str, str]  # question_id → option_id
    recommendation_text: str
    priority: int
    active: bool = True
    sets_urgency: Optional[UrgencyLevel] = None


@dataclass
class AnswerSnapshot:
    question_id: str
    question_label: str
    option_id: str
    option_label: str
    option_code: str


@dataclass
class StatusHistoryEntry:
    status: TicketStatus
    at: datetime
    note: Optional[str] = None


@dataclass
class Ticket:
    id: str
    resident_ref: str
    building_id: str
    address_snapshot: str
    organization_id: str
    parent_category_id: str
    category_id: str
    answers_snapshot: list[AnswerSnapshot]
    recommendation_text_snapshot: str
    urgency_level: UrgencyLevel
    summary_text: str
    status: TicketStatus = TicketStatus.NEW
    photo_url: Optional[str] = None
    assignee_specialist_id: Optional[str] = None
    taken_by_dispatcher_id: Optional[str] = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    status_history: list[StatusHistoryEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.status_history:
            self.status_history = [
                StatusHistoryEntry(status=TicketStatus.NEW, at=self.created_at, note="Создана")
            ]

    def _transition(self, new_status: TicketStatus, note: Optional[str] = None) -> None:
        self.status = new_status
        self.updated_at = _utcnow()
        self.status_history.append(
            StatusHistoryEntry(status=new_status, at=self.updated_at, note=note)
        )

    def accept(self, dispatcher_id: str) -> None:
        if self.status != TicketStatus.NEW:
            raise InvalidTicketTransitionError(
                "Принять можно только новую заявку"
            )
        self.taken_by_dispatcher_id = dispatcher_id
        self._transition(TicketStatus.ACCEPTED, note=f"Принята диспетчером {dispatcher_id}")

    def assign_specialist(self, specialist: Specialist) -> None:
        if specialist.organization_id != self.organization_id:
            raise OrganizationMismatchError(
                "Специалист принадлежит другой организации"
            )
        if self.status not in (TicketStatus.ACCEPTED, TicketStatus.IN_PROGRESS):
            raise InvalidTicketTransitionError(
                "Назначить специалиста можно только для принятой или уже в работе заявки"
            )
        if not specialist.active:
            raise InvalidTicketTransitionError("Специалист неактивен")
        self.assignee_specialist_id = specialist.id
        if self.status == TicketStatus.ACCEPTED:
            self._transition(
                TicketStatus.IN_PROGRESS,
                note=f"Назначен специалист {specialist.full_name}",
            )
        else:
            self.updated_at = _utcnow()
            self.status_history.append(
                StatusHistoryEntry(
                    status=TicketStatus.IN_PROGRESS,
                    at=self.updated_at,
                    note=f"Переназначен специалист {specialist.full_name}",
                )
            )

    def complete(self) -> None:
        if self.status != TicketStatus.IN_PROGRESS:
            raise InvalidTicketTransitionError(
                "Завершить можно только заявку в работе"
            )
        self._transition(TicketStatus.DONE, note="Выполнена")

    def cancel_by_resident(self) -> None:
        if self.status not in (TicketStatus.NEW, TicketStatus.ACCEPTED):
            raise InvalidTicketTransitionError(
                "Отменить можно только новую или принятую заявку"
            )
        self._transition(TicketStatus.CANCELLED_BY_RESIDENT, note="Отменена жителем")


@dataclass
class DispatcherAccount:
    id: str
    username: str
    password_hash: str
    organization_id: str
    full_name: str = ""
