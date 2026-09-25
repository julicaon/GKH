from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from application.ports.building_repository import BuildingRepository
from application.ports.category_repository import CategoryRepository
from application.ports.organization_repository import OrganizationRepository
from application.ports.specialist_repository import SpecialistRepository
from application.ports.ticket_repository import TicketRepository
from application.ports.unit_of_work import UnitOfWork
from domain.entities import (
    Building,
    Category,
    DispatcherAccount,
    Option,
    Organization,
    ParentCategory,
    Question,
    RecommendationRule,
    Specialist,
    Ticket,
)
from domain.enums import UrgencyLevel
from infrastructure.persistence import mappers
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


class SqlBuildingRepository(BuildingRepository):
    def __init__(self, session: Session):
        self._s = session

    def list_all(self) -> list[Building]:
        rows = self._s.query(BuildingModel).all()
        return [mappers.building_to_domain(r) for r in rows]

    def get_by_id(self, building_id: str) -> Optional[Building]:
        row = self._s.get(BuildingModel, building_id)
        return mappers.building_to_domain(row) if row else None

    def add(self, building: Building) -> Building:
        m = BuildingModel(
            id=building.id,
            address_label=building.address_label,
            organization_id=building.organization_id,
            available_parent_category_ids=building.available_parent_category_ids,
            available_category_ids=building.available_category_ids,
        )
        self._s.add(m)
        self._s.flush()
        return building


class SqlCategoryRepository(CategoryRepository):
    def __init__(self, session: Session):
        self._s = session

    def add_parent(self, parent: ParentCategory) -> ParentCategory:
        m = ParentCategoryModel(
            id=parent.id,
            name=parent.name,
            order=parent.order,
            active=parent.active,
            default_urgency_hint=parent.default_urgency_hint.value,
        )
        self._s.add(m)
        self._s.flush()
        return parent

    def get_parent(self, parent_id: str) -> Optional[ParentCategory]:
        row = self._s.get(ParentCategoryModel, parent_id)
        return mappers.parent_to_domain(row) if row else None

    def list_parents(self, active_only: bool = False) -> list[ParentCategory]:
        q = self._s.query(ParentCategoryModel)
        if active_only:
            q = q.filter(ParentCategoryModel.active.is_(True))
        return [mappers.parent_to_domain(r) for r in q.all()]

    def add_category(self, category: Category) -> Category:
        m = CategoryModel(
            id=category.id,
            parent_category_id=category.parent_category_id,
            name=category.name,
            active=category.active,
            order=category.order,
            default_recommendation_text=category.default_recommendation_text,
            default_urgency=category.default_urgency.value,
            organization_ids=category.organization_ids,
        )
        self._s.add(m)
        self._s.flush()
        return category

    def get_category(self, category_id: str) -> Optional[Category]:
        row = self._s.get(CategoryModel, category_id)
        return mappers.category_to_domain(row) if row else None

    def update_category(self, category: Category) -> Category:
        row = self._s.get(CategoryModel, category.id)
        if not row:
            raise ValueError("category not found")
        row.name = category.name
        row.active = category.active
        row.order = category.order
        row.default_recommendation_text = category.default_recommendation_text
        row.default_urgency = category.default_urgency.value
        row.organization_ids = category.organization_ids
        self._s.flush()
        return category

    def list_categories(
        self, parent_id: Optional[str] = None, active_only: bool = False
    ) -> list[Category]:
        q = self._s.query(CategoryModel)
        if parent_id:
            q = q.filter(CategoryModel.parent_category_id == parent_id)
        if active_only:
            q = q.filter(CategoryModel.active.is_(True))
        return [mappers.category_to_domain(r) for r in q.all()]

    def add_question(self, question: Question) -> Question:
        m = QuestionModel(
            id=question.id,
            category_id=question.category_id,
            text=question.text,
            order=question.order,
            active=question.active,
            options=[{"id": o.id, "label": o.label, "code": o.code} for o in question.options],
        )
        self._s.add(m)
        self._s.flush()
        return question

    def get_question(self, question_id: str) -> Optional[Question]:
        row = self._s.get(QuestionModel, question_id)
        return mappers.question_to_domain(row) if row else None

    def list_questions(self, category_id: str, active_only: bool = False) -> list[Question]:
        q = self._s.query(QuestionModel).filter(QuestionModel.category_id == category_id)
        if active_only:
            q = q.filter(QuestionModel.active.is_(True))
        return [mappers.question_to_domain(r) for r in q.all()]

    def add_option_to_question(
        self, question_id: str, option_id: str, label: str, code: str
    ) -> Question:
        row = self._s.get(QuestionModel, question_id)
        if not row:
            raise ValueError("question not found")
        opts = list(row.options or [])
        opts.append({"id": option_id, "label": label, "code": code})
        row.options = opts
        self._s.flush()
        return mappers.question_to_domain(row)

    def upsert_rule(self, rule: RecommendationRule) -> RecommendationRule:
        row = self._s.get(RecommendationRuleModel, rule.id)
        if row:
            row.category_id = rule.category_id
            row.match = rule.match
            row.recommendation_text = rule.recommendation_text
            row.priority = rule.priority
            row.active = rule.active
            row.sets_urgency = rule.sets_urgency.value if rule.sets_urgency else None
        else:
            row = RecommendationRuleModel(
                id=rule.id,
                category_id=rule.category_id,
                match=rule.match,
                recommendation_text=rule.recommendation_text,
                priority=rule.priority,
                active=rule.active,
                sets_urgency=rule.sets_urgency.value if rule.sets_urgency else None,
            )
            self._s.add(row)
        self._s.flush()
        return rule

    def list_rules(
        self, category_id: str, active_only: bool = False
    ) -> list[RecommendationRule]:
        q = self._s.query(RecommendationRuleModel).filter(
            RecommendationRuleModel.category_id == category_id
        )
        if active_only:
            q = q.filter(RecommendationRuleModel.active.is_(True))
        return [mappers.rule_to_domain(r) for r in q.all()]

    def get_rule(self, rule_id: str) -> Optional[RecommendationRule]:
        row = self._s.get(RecommendationRuleModel, rule_id)
        return mappers.rule_to_domain(row) if row else None


class SqlTicketRepository(TicketRepository):
    def __init__(self, session: Session):
        self._s = session

    def add(self, ticket: Ticket) -> Ticket:
        fields = mappers.ticket_to_model_fields(ticket)
        self._s.add(TicketModel(**fields))
        self._s.flush()
        return ticket

    def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        row = self._s.get(TicketModel, ticket_id)
        return mappers.ticket_to_domain(row) if row else None

    def update(self, ticket: Ticket) -> Ticket:
        row = self._s.get(TicketModel, ticket.id)
        if not row:
            raise ValueError("ticket not found")
        fields = mappers.ticket_to_model_fields(ticket)
        for k, v in fields.items():
            if k != "id":
                setattr(row, k, v)
        self._s.flush()
        return ticket

    def list_for_org(self, organization_id: str) -> list[Ticket]:
        rows = (
            self._s.query(TicketModel)
            .filter(TicketModel.organization_id == organization_id)
            .all()
        )
        tickets = [mappers.ticket_to_domain(r) for r in rows]
        urgency_rank = {UrgencyLevel.HIGH: 0, UrgencyLevel.MEDIUM: 1, UrgencyLevel.LOW: 2}
        tickets.sort(key=lambda t: (urgency_rank[t.urgency_level], -t.created_at.timestamp()))
        return tickets

    def list_for_resident(self, resident_ref: str) -> list[Ticket]:
        rows = (
            self._s.query(TicketModel)
            .filter(TicketModel.resident_ref == resident_ref)
            .order_by(TicketModel.created_at.desc())
            .all()
        )
        return [mappers.ticket_to_domain(r) for r in rows]


class SqlSpecialistRepository(SpecialistRepository):
    def __init__(self, session: Session):
        self._s = session

    def add(self, specialist: Specialist) -> Specialist:
        m = SpecialistModel(
            id=specialist.id,
            organization_id=specialist.organization_id,
            full_name=specialist.full_name,
            skill_tags=specialist.skill_tags,
            active=specialist.active,
        )
        self._s.add(m)
        self._s.flush()
        return specialist

    def get_by_id(self, specialist_id: str) -> Optional[Specialist]:
        row = self._s.get(SpecialistModel, specialist_id)
        return mappers.specialist_to_domain(row) if row else None

    def update(self, specialist: Specialist) -> Specialist:
        row = self._s.get(SpecialistModel, specialist.id)
        if not row:
            raise ValueError("specialist not found")
        row.full_name = specialist.full_name
        row.skill_tags = specialist.skill_tags
        row.active = specialist.active
        self._s.flush()
        return specialist

    def list_for_org(
        self, organization_id: str, active_only: bool = False
    ) -> list[Specialist]:
        q = self._s.query(SpecialistModel).filter(
            SpecialistModel.organization_id == organization_id
        )
        if active_only:
            q = q.filter(SpecialistModel.active.is_(True))
        return [mappers.specialist_to_domain(r) for r in q.all()]


class SqlOrganizationRepository(OrganizationRepository):
    def __init__(self, session: Session):
        self._s = session

    def add(self, org: Organization) -> Organization:
        self._s.add(OrganizationModel(id=org.id, name=org.name))
        self._s.flush()
        return org

    def get_by_id(self, org_id: str) -> Optional[Organization]:
        row = self._s.get(OrganizationModel, org_id)
        return mappers.org_to_domain(row) if row else None

    def list_all(self) -> list[Organization]:
        return [mappers.org_to_domain(r) for r in self._s.query(OrganizationModel).all()]

    def add_dispatcher(self, account: DispatcherAccount) -> DispatcherAccount:
        self._s.add(
            DispatcherModel(
                id=account.id,
                username=account.username,
                password_hash=account.password_hash,
                organization_id=account.organization_id,
                full_name=account.full_name,
            )
        )
        self._s.flush()
        return account

    def get_dispatcher_by_username(self, username: str) -> Optional[DispatcherAccount]:
        row = (
            self._s.query(DispatcherModel)
            .filter(DispatcherModel.username == username)
            .one_or_none()
        )
        return mappers.dispatcher_to_domain(row) if row else None

    def get_dispatcher(self, dispatcher_id: str) -> Optional[DispatcherAccount]:
        row = self._s.get(DispatcherModel, dispatcher_id)
        return mappers.dispatcher_to_domain(row) if row else None


class SqlUnitOfWork(UnitOfWork):
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session: Optional[Session] = None

    def __enter__(self) -> "SqlUnitOfWork":
        self._session = self._session_factory()
        self.buildings = SqlBuildingRepository(self._session)
        self.categories = SqlCategoryRepository(self._session)
        self.tickets = SqlTicketRepository(self._session)
        self.specialists = SqlSpecialistRepository(self._session)
        self.organizations = SqlOrganizationRepository(self._session)
        return self

    def commit(self) -> None:
        if self._session:
            self._session.commit()

    def rollback(self) -> None:
        if self._session:
            self._session.rollback()

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type:
                self.rollback()
            else:
                self.commit()
        finally:
            if self._session:
                self._session.close()
                self._session = None
