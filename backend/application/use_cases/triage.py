from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from application.ports.building_repository import BuildingRepository
from application.ports.category_repository import CategoryRepository
from domain.entities import Category, Option, ParentCategory, Question, RecommendationRule, new_id
from domain.enums import UrgencyLevel
from domain.exceptions import BuildingNotFoundError, CategoryNotFoundError, ValidationError


@dataclass
class CreateParentCategory:
    categories: CategoryRepository

    def execute(
        self,
        name: str,
        order: int = 0,
        active: bool = True,
        default_urgency_hint: UrgencyLevel = UrgencyLevel.MEDIUM,
        id: Optional[str] = None,
    ) -> ParentCategory:
        parent = ParentCategory(
            id=id or new_id(),
            name=name,
            order=order,
            active=active,
            default_urgency_hint=default_urgency_hint,
        )
        return self.categories.add_parent(parent)


@dataclass
class CreateCategory:
    categories: CategoryRepository

    def execute(
        self,
        parent_category_id: str,
        name: str,
        order: int = 0,
        active: bool = True,
        default_recommendation_text: str = "",
        default_urgency: UrgencyLevel = UrgencyLevel.MEDIUM,
        organization_ids: Optional[list[str]] = None,
        id: Optional[str] = None,
    ) -> Category:
        parent = self.categories.get_parent(parent_category_id)
        if not parent:
            raise CategoryNotFoundError(f"Родительская категория {parent_category_id} не найдена")
        category = Category(
            id=id or new_id(),
            parent_category_id=parent_category_id,
            name=name,
            active=active,
            order=order,
            default_recommendation_text=default_recommendation_text,
            default_urgency=default_urgency,
            organization_ids=organization_ids,
        )
        return self.categories.add_category(category)


@dataclass
class UpdateCategory:
    categories: CategoryRepository

    def execute(
        self,
        category_id: str,
        name: Optional[str] = None,
        active: Optional[bool] = None,
        order: Optional[int] = None,
        default_recommendation_text: Optional[str] = None,
        default_urgency: Optional[UrgencyLevel] = None,
        organization_ids: Optional[list[str]] = None,
    ) -> Category:
        category = self.categories.get_category(category_id)
        if not category:
            raise CategoryNotFoundError(f"Категория {category_id} не найдена")
        if name is not None:
            category.name = name
        if active is not None:
            category.active = active
        if order is not None:
            category.order = order
        if default_recommendation_text is not None:
            category.default_recommendation_text = default_recommendation_text
        if default_urgency is not None:
            category.default_urgency = default_urgency
        if organization_ids is not None:
            category.organization_ids = organization_ids
        return self.categories.update_category(category)


@dataclass
class ListAvailableCategoriesForBuilding:
    buildings: BuildingRepository
    categories: CategoryRepository

    def execute(self, building_id: str) -> dict:
        building = self.buildings.get_by_id(building_id)
        if not building:
            raise BuildingNotFoundError(f"Дом с id={building_id} не найден")

        parents = self.categories.list_parents(active_only=True)
        if building.available_parent_category_ids is not None:
            allowed = set(building.available_parent_category_ids)
            parents = [p for p in parents if p.id in allowed]

        result_parents = []
        for parent in sorted(parents, key=lambda p: p.order):
            leafs = self.categories.list_categories(parent_id=parent.id, active_only=True)
            if building.available_category_ids is not None:
                allowed_cats = set(building.available_category_ids)
                leafs = [c for c in leafs if c.id in allowed_cats]
            # Filter by organization if category has organization_ids
            leafs = [
                c
                for c in leafs
                if c.organization_ids is None
                or building.organization_id in c.organization_ids
            ]
            leafs = sorted(leafs, key=lambda c: c.order)
            result_parents.append({"parent": parent, "categories": leafs})
        return {"building": building, "tree": result_parents}


@dataclass
class AddQuestion:
    categories: CategoryRepository

    def execute(
        self,
        category_id: str,
        text: str,
        order: int = 0,
        active: bool = True,
        options: Optional[list[dict]] = None,
        id: Optional[str] = None,
    ) -> Question:
        category = self.categories.get_category(category_id)
        if not category:
            raise CategoryNotFoundError(f"Категория {category_id} не найдена")
        opts = []
        for o in options or []:
            opts.append(
                Option(
                    id=o.get("id") or new_id(),
                    label=o["label"],
                    code=o["code"],
                )
            )
        question = Question(
            id=id or new_id(),
            category_id=category_id,
            text=text,
            order=order,
            active=active,
            options=opts,
        )
        return self.categories.add_question(question)


@dataclass
class AddOption:
    categories: CategoryRepository

    def execute(
        self,
        question_id: str,
        label: str,
        code: str,
        id: Optional[str] = None,
    ) -> Question:
        question = self.categories.get_question(question_id)
        if not question:
            raise ValidationError(f"Вопрос {question_id} не найден")
        return self.categories.add_option_to_question(
            question_id=question_id,
            option_id=id or new_id(),
            label=label,
            code=code,
        )


@dataclass
class UpsertRecommendationRule:
    categories: CategoryRepository

    def execute(
        self,
        category_id: str,
        match: dict[str, str],
        recommendation_text: str,
        priority: int,
        active: bool = True,
        sets_urgency: Optional[UrgencyLevel] = None,
        id: Optional[str] = None,
    ) -> RecommendationRule:
        category = self.categories.get_category(category_id)
        if not category:
            raise CategoryNotFoundError(f"Категория {category_id} не найдена")
        rule = RecommendationRule(
            id=id or new_id(),
            category_id=category_id,
            match=match,
            recommendation_text=recommendation_text,
            priority=priority,
            active=active,
            sets_urgency=sets_urgency,
        )
        return self.categories.upsert_rule(rule)


@dataclass
class GetCategoryQuestionnaire:
    categories: CategoryRepository

    def execute(self, category_id: str) -> dict:
        category = self.categories.get_category(category_id)
        if not category:
            raise CategoryNotFoundError(f"Категория {category_id} не найдена")
        parent = self.categories.get_parent(category.parent_category_id)
        questions = self.categories.list_questions(category_id, active_only=True)
        questions = sorted(questions, key=lambda q: q.order)
        rules = self.categories.list_rules(category_id, active_only=True)
        return {
            "category": category,
            "parent": parent,
            "questions": questions,
            "rules": rules,
        }


@dataclass
class ListParentCategories:
    categories: CategoryRepository

    def execute(self, active_only: bool = False) -> list[ParentCategory]:
        return self.categories.list_parents(active_only=active_only)


@dataclass
class ListCategories:
    categories: CategoryRepository

    def execute(
        self, parent_id: Optional[str] = None, active_only: bool = False
    ) -> list[Category]:
        return self.categories.list_categories(parent_id=parent_id, active_only=active_only)
