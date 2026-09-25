from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from application.ports.organization_repository import OrganizationRepository
from application.ports.specialist_repository import SpecialistRepository
from domain.entities import Specialist, new_id
from domain.exceptions import SpecialistNotFoundError, ValidationError


@dataclass
class ListSpecialists:
    specialists: SpecialistRepository

    def execute(self, organization_id: str, active_only: bool = False) -> list[Specialist]:
        return self.specialists.list_for_org(organization_id, active_only=active_only)


@dataclass
class CreateSpecialist:
    specialists: SpecialistRepository
    organizations: OrganizationRepository

    def execute(
        self,
        organization_id: str,
        full_name: str,
        skill_tags: Optional[list[str]] = None,
        active: bool = True,
        id: Optional[str] = None,
    ) -> Specialist:
        org = self.organizations.get_by_id(organization_id)
        if not org:
            raise ValidationError(f"Организация {organization_id} не найдена")
        specialist = Specialist(
            id=id or new_id(),
            organization_id=organization_id,
            full_name=full_name,
            skill_tags=skill_tags or [],
            active=active,
        )
        return self.specialists.add(specialist)


@dataclass
class UpdateSpecialist:
    specialists: SpecialistRepository

    def execute(
        self,
        specialist_id: str,
        full_name: Optional[str] = None,
        skill_tags: Optional[list[str]] = None,
        active: Optional[bool] = None,
    ) -> Specialist:
        specialist = self.specialists.get_by_id(specialist_id)
        if not specialist:
            raise SpecialistNotFoundError(f"Специалист {specialist_id} не найден")
        if full_name is not None:
            specialist.full_name = full_name
        if skill_tags is not None:
            specialist.skill_tags = skill_tags
        if active is not None:
            specialist.active = active
        return self.specialists.update(specialist)
