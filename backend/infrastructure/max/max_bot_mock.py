from typing import Any

from application.ports.max_ports import MaxBotPort


class MaxBotMock(MaxBotPort):
    def __init__(self) -> None:
        self.outbox: list[dict[str, Any]] = []

    def send_message(self, chat_id: str, text: str) -> bool:
        self.outbox.append({"chat_id": chat_id, "text": text, "type": "message"})
        return True

    def handle_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.outbox.append({"type": "webhook", "payload": payload})
        return {"ok": True, "handled": True, "mode": "mock"}

    def get_outbox(self) -> list[dict[str, Any]]:
        return list(self.outbox)
