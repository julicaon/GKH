from abc import ABC, abstractmethod
from typing import Optional

from domain.entities import DispatcherAccount, Organization


class OrganizationRepository(ABC):
    @abstractmethod
    def add(self, org: Organization) -> Organization:
        ...

    @abstractmethod
    def get_by_id(self, org_id: str) -> Optional[Organization]:
        ...

    @abstractmethod
    def list_all(self) -> list[Organization]:
        ...

    @abstractmethod
    def add_dispatcher(self, account: DispatcherAccount) -> DispatcherAccount:
        ...

    @abstractmethod
    def get_dispatcher_by_username(self, username: str) -> Optional[DispatcherAccount]:
        ...

    @abstractmethod
    def get_dispatcher(self, dispatcher_id: str) -> Optional[DispatcherAccount]:
        ...
