from typing import Any

from application.ports.max_ports import MaxBridgePort


class MaxBridgeReal(MaxBridgePort):
    def __init__(self, token: str):
        self.token = token

    def resolve_user(self, max_user_id: str) -> dict[str, Any]:
        return {
            "id": max_user_id,
            "display_name": max_user_id,
            "source": "real",
        }

    def notify_user(self, max_user_id: str, message: str) -> bool:
        if not self.token:
            return False
        return True
