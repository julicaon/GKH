from abc import ABC, abstractmethod
from typing import Optional

from domain.entities import Ticket
from domain.enums import UrgencyLevel


class TicketRepository(ABC):
    @abstractmethod
    def add(self, ticket: Ticket) -> Ticket:
        ...

    @abstractmethod
    def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        ...

    @abstractmethod
    def update(self, ticket: Ticket) -> Ticket:
        ...

    @abstractmethod
    def list_for_org(self, organization_id: str) -> list[Ticket]:
        """HIGH first, then created_at desc."""
        ...

    @abstractmethod
    def list_for_resident(self, resident_ref: str) -> list[Ticket]:
        ...
