from dataclasses import dataclass
from typing import Optional

from application.ports.building_repository import BuildingRepository
from domain.entities import Building
from domain.exceptions import BuildingNotFoundError, ValidationError


@dataclass
class ListBuildingsForResident:
    buildings: BuildingRepository

    def execute(self) -> list[Building]:
        return self.buildings.list_all()


@dataclass
class ResolveBuilding:
    """Resolve by id or free-text address → nearest seed Building."""

    buildings: BuildingRepository

    def execute(
        self,
        building_id: Optional[str] = None,
        address_query: Optional[str] = None,
    ) -> Building:
        if building_id:
            building = self.buildings.get_by_id(building_id)
            if not building:
                raise BuildingNotFoundError(f"Дом с id={building_id} не найден")
            return building

        query = (address_query or "").strip().lower()
        if not query:
            raise ValidationError("Укажите buildingId или addressQuery")

        all_buildings = self.buildings.list_all()
        # Exact / substring match first
        for b in all_buildings:
            label = b.address_label.lower()
            if query == label or query in label or label in query:
                return b

        # Token overlap (улица / дом)
        tokens = [t for t in query.replace(",", " ").split() if len(t) > 1]
        best: Optional[Building] = None
        best_score = 0
        for b in all_buildings:
            label = b.address_label.lower()
            score = sum(1 for t in tokens if t in label)
            if score > best_score:
                best_score = score
                best = b

        if best and best_score > 0:
            return best

        raise BuildingNotFoundError(
            f"Не удалось сопоставить адрес «{address_query}» с модельным домом"
        )
