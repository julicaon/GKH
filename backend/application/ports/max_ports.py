from abc import ABC, abstractmethod
from typing import Any, Optional


class MaxBridgePort(ABC):
    """Bridge to MAX messenger user/chat context."""

    @abstractmethod
    def resolve_user(self, max_user_id: str) -> dict[str, Any]:
        ...

    @abstractmethod
    def notify_user(self, max_user_id: str, message: str) -> bool:
        ...


class MaxBotPort(ABC):
    """Outbound bot messages / webhook handling."""

    @abstractmethod
    def send_message(self, chat_id: str, text: str) -> bool:
        ...

    @abstractmethod
    def handle_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_outbox(self) -> list[dict[str, Any]]:
        ...
