from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class DispatcherModel(Base):
    __tablename__ = "dispatchers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), default="")


class SpecialistModel(Base):
    __tablename__ = "specialists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    skill_tags: Mapped[list] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class BuildingModel(Base):
    __tablename__ = "buildings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    address_label: Mapped[str] = mapped_column(String(512), nullable=False)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id"), nullable=False
    )
    available_parent_category_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    available_category_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)


class ParentCategoryModel(Base):
    __tablename__ = "parent_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    default_urgency_hint: Mapped[str] = mapped_column(String(20), default="MEDIUM")


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    parent_category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("parent_categories.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    default_recommendation_text: Mapped[str] = mapped_column(Text, default="")
    default_urgency: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    organization_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)


class QuestionModel(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    options: Mapped[list] = mapped_column(JSON, default=list)


class RecommendationRuleModel(Base):
    __tablename__ = "recommendation_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=False
    )
    match: Mapped[dict] = mapped_column(JSON, default=dict)
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    sets_urgency: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class TicketModel(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    resident_ref: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    building_id: Mapped[str] = mapped_column(String(36), nullable=False)
    address_snapshot: Mapped[str] = mapped_column(String(512), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    parent_category_id: Mapped[str] = mapped_column(String(36), nullable=False)
    category_id: Mapped[str] = mapped_column(String(36), nullable=False)
    answers_snapshot: Mapped[list] = mapped_column(JSON, default=list)
    recommendation_text_snapshot: Mapped[str] = mapped_column(Text, default="")
    urgency_level: Mapped[str] = mapped_column(String(20), nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="NEW")
    photo_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assignee_specialist_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    taken_by_dispatcher_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status_history: Mapped[list] = mapped_column(JSON, default=list)


def make_engine(database_url: str):
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, connect_args=connect_args, future=True)


def make_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
