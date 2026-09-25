from typing import Any

from application.ports.max_ports import MaxBridgePort


class MaxBridgeMock(MaxBridgePort):
    def resolve_user(self, max_user_id: str) -> dict[str, Any]:
        return {
            "id": max_user_id,
            "display_name": f"Житель {max_user_id}",
            "source": "mock",
        }

    def notify_user(self, max_user_id: str, message: str) -> bool:
        return True
