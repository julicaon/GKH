from abc import ABC, abstractmethod
from typing import Optional

from domain.entities import Category, ParentCategory, Question, RecommendationRule


class CategoryRepository(ABC):
    @abstractmethod
    def add_parent(self, parent: ParentCategory) -> ParentCategory:
        ...

    @abstractmethod
    def get_parent(self, parent_id: str) -> Optional[ParentCategory]:
        ...

    @abstractmethod
    def list_parents(self, active_only: bool = False) -> list[ParentCategory]:
        ...

    @abstractmethod
    def add_category(self, category: Category) -> Category:
        ...

    @abstractmethod
    def get_category(self, category_id: str) -> Optional[Category]:
        ...

    @abstractmethod
    def update_category(self, category: Category) -> Category:
        ...

    @abstractmethod
    def list_categories(
        self,
        parent_id: Optional[str] = None,
        active_only: bool = False,
    ) -> list[Category]:
        ...

    @abstractmethod
    def add_question(self, question: Question) -> Question:
        ...

    @abstractmethod
    def get_question(self, question_id: str) -> Optional[Question]:
        ...

    @abstractmethod
    def list_questions(self, category_id: str, active_only: bool = False) -> list[Question]:
        ...

    @abstractmethod
    def add_option_to_question(
        self, question_id: str, option_id: str, label: str, code: str
    ) -> Question:
        ...

    @abstractmethod
    def upsert_rule(self, rule: RecommendationRule) -> RecommendationRule:
        ...

    @abstractmethod
    def list_rules(self, category_id: str, active_only: bool = False) -> list[RecommendationRule]:
        ...

    @abstractmethod
    def get_rule(self, rule_id: str) -> Optional[RecommendationRule]:
        ...
