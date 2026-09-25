from abc import ABC, abstractmethod
from typing import Optional

from domain.entities import Building


class BuildingRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Building]:
        ...

    @abstractmethod
    def get_by_id(self, building_id: str) -> Optional[Building]:
        ...

    @abstractmethod
    def add(self, building: Building) -> Building:
        ...
