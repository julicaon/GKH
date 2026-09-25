from abc import ABC, abstractmethod
from typing import Optional

from domain.entities import Specialist


class SpecialistRepository(ABC):
    @abstractmethod
    def add(self, specialist: Specialist) -> Specialist:
        ...

    @abstractmethod
    def get_by_id(self, specialist_id: str) -> Optional[Specialist]:
        ...

    @abstractmethod
    def update(self, specialist: Specialist) -> Specialist:
        ...

    @abstractmethod
    def list_for_org(self, organization_id: str, active_only: bool = False) -> list[Specialist]:
        ...
