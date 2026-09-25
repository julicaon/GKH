from dataclasses import dataclass
from typing import Optional

from application.ports.building_repository import BuildingRepository
from domain.entities import Building
from domain.exceptions import BuildingNotFoundError


@dataclass
class ListBuildingsForResident:
    buildings: BuildingRepository

    def execute(self) -> list[Building]:
        return self.buildings.list_all()


@dataclass
class ResolveBuilding:
    buildings: BuildingRepository

    def execute(self, building_id: str) -> Building:
        building = self.buildings.get_by_id(building_id)
        if not building:
            raise BuildingNotFoundError(f"Дом с id={building_id} не найден")
        return building
