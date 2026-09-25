from abc import ABC, abstractmethod

from application.ports.building_repository import BuildingRepository
from application.ports.category_repository import CategoryRepository
from application.ports.organization_repository import OrganizationRepository
from application.ports.specialist_repository import SpecialistRepository
from application.ports.ticket_repository import TicketRepository


class UnitOfWork(ABC):
    buildings: BuildingRepository
    categories: CategoryRepository
    tickets: TicketRepository
    specialists: SpecialistRepository
    organizations: OrganizationRepository

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()
