from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from application.ports.building_repository import BuildingRepository
from application.ports.category_repository import CategoryRepository
from application.ports.max_ports import MaxBotPort
from application.ports.specialist_repository import SpecialistRepository
from application.ports.ticket_repository import TicketRepository
from domain.entities import AnswerSnapshot, Ticket, new_id
from domain.enums import TicketStatus
from domain.exceptions import (
    BuildingNotFoundError,
    CategoryNotFoundError,
    SpecialistNotFoundError,
    TicketNotFoundError,
    ValidationError,
)
from domain.services import build_summary_text, compute_urgency, match_recommendation


@dataclass
class SubmitTicket:
    buildings: BuildingRepository
    categories: CategoryRepository
    tickets: TicketRepository
    max_bot: Optional[MaxBotPort] = None

    def execute(
        self,
        building_id: str,
        category_id: str,
        answers: dict[str, str],  # question_id → option_id
        resident_ref: str,
        photo_url: Optional[str] = None,
    ) -> Ticket:
        building = self.buildings.get_by_id(building_id)
        if not building:
            raise BuildingNotFoundError(f"Дом с id={building_id} не найден")

        category = self.categories.get_category(category_id)
        if not category:
            raise CategoryNotFoundError(f"Категория {category_id} не найдена")

        if not category.active:
            raise ValidationError("Категория неактивна")

        # Building category availability
        if building.available_category_ids is not None:
            if category_id not in building.available_category_ids:
                raise ValidationError("Категория недоступна для этого дома")
        if building.available_parent_category_ids is not None:
            if category.parent_category_id not in building.available_parent_category_ids:
                raise ValidationError("Родительская категория недоступна для этого дома")

        questions = self.categories.list_questions(category_id, active_only=True)
        q_map = {q.id: q for q in questions}
        option_lookup: dict[str, tuple] = {}
        for q in questions:
            for o in q.options:
                option_lookup[o.id] = (q, o)

        snapshots: list[AnswerSnapshot] = []
        for qid, oid in answers.items():
            if qid not in q_map:
                raise ValidationError(f"Вопрос {qid} не относится к категории")
            if oid not in option_lookup:
                raise ValidationError(f"Вариант ответа {oid} не найден")
            q, o = option_lookup[oid]
            if q.id != qid:
                raise ValidationError("Вариант ответа не соответствует вопросу")
            snapshots.append(
                AnswerSnapshot(
                    question_id=qid,
                    question_label=q.text,
                    option_id=oid,
                    option_label=o.label,
                    option_code=o.code,
                )
            )

        rules = self.categories.list_rules(category_id, active_only=True)
        rec_text, matched = match_recommendation(
            rules, answers, category.default_recommendation_text
        )
        codes = [s.option_code for s in snapshots]
        urgency = compute_urgency(
            category.default_urgency,
            matched.sets_urgency if matched else None,
            codes,
        )
        summary = build_summary_text(category.name, snapshots, rec_text)

        ticket = Ticket(
            id=new_id(),
            resident_ref=resident_ref,
            building_id=building.id,
            address_snapshot=building.address_label,
            organization_id=building.organization_id,
            parent_category_id=category.parent_category_id,
            category_id=category.id,
            answers_snapshot=snapshots,
            recommendation_text_snapshot=rec_text,
            urgency_level=urgency,
            summary_text=summary,
            photo_url=photo_url,
            status=TicketStatus.NEW,
        )
        saved = self.tickets.add(ticket)
        if self.max_bot:
            self.max_bot.send_message(
                resident_ref,
                f"Заявка создана: {summary}",
            )
        return saved


@dataclass
class GetTicket:
    tickets: TicketRepository

    def execute(self, ticket_id: str) -> Ticket:
        ticket = self.tickets.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(f"Заявка {ticket_id} не найдена")
        return ticket


@dataclass
class ListTicketsForOrg:
    tickets: TicketRepository

    def execute(self, organization_id: str) -> list[Ticket]:
        return self.tickets.list_for_org(organization_id)


@dataclass
class ListTicketsForResident:
    tickets: TicketRepository

    def execute(self, resident_ref: str) -> list[Ticket]:
        return self.tickets.list_for_resident(resident_ref)


@dataclass
class AcceptTicket:
    tickets: TicketRepository

    def execute(
        self,
        ticket_id: str,
        dispatcher_id: str,
        organization_id: Optional[str] = None,
    ) -> Ticket:
        ticket = self.tickets.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(f"Заявка {ticket_id} не найдена")
        if organization_id and ticket.organization_id != organization_id:
            raise ValidationError("Заявка принадлежит другой УК")
        ticket.accept(dispatcher_id)
        return self.tickets.update(ticket)


@dataclass
class AssignSpecialist:
    tickets: TicketRepository
    specialists: SpecialistRepository

    def execute(
        self,
        ticket_id: str,
        specialist_id: str,
        organization_id: Optional[str] = None,
    ) -> Ticket:
        ticket = self.tickets.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(f"Заявка {ticket_id} не найдена")
        if organization_id and ticket.organization_id != organization_id:
            raise ValidationError("Заявка принадлежит другой УК")
        specialist = self.specialists.get_by_id(specialist_id)
        if not specialist:
            raise SpecialistNotFoundError(f"Специалист {specialist_id} не найден")
        ticket.assign_specialist(specialist)
        return self.tickets.update(ticket)


@dataclass
class CompleteTicket:
    tickets: TicketRepository

    def execute(
        self,
        ticket_id: str,
        organization_id: Optional[str] = None,
    ) -> Ticket:
        ticket = self.tickets.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(f"Заявка {ticket_id} не найдена")
        if organization_id and ticket.organization_id != organization_id:
            raise ValidationError("Заявка принадлежит другой УК")
        ticket.complete()
        return self.tickets.update(ticket)


@dataclass
class CancelTicketByResident:
    tickets: TicketRepository

    def execute(
        self,
        ticket_id: str,
        reason: str,
        resident_ref: Optional[str] = None,
    ) -> Ticket:
        ticket = self.tickets.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(f"Заявка {ticket_id} не найдена")
        if resident_ref and ticket.resident_ref != resident_ref:
            raise ValidationError("Нельзя отменить чужую заявку")
        ticket.cancel_by_resident(reason)
        return self.tickets.update(ticket)
