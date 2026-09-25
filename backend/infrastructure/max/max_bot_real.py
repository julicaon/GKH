from typing import Any

from application.ports.max_ports import MaxBotPort


class MaxBotReal(MaxBotPort):
    def __init__(self, token: str):
        self.token = token
        self.outbox: list[dict[str, Any]] = []

    def send_message(self, chat_id: str, text: str) -> bool:
        self.outbox.append(
            {"chat_id": chat_id, "text": text, "type": "message", "mode": "real"}
        )
        return bool(self.token)

    def handle_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.outbox.append({"type": "webhook", "payload": payload})
        return {"ok": True, "handled": True, "mode": "real"}

    def get_outbox(self) -> list[dict[str, Any]]:
        return list(self.outbox)
