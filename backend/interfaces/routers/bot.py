from typing import Any

from fastapi import APIRouter, Depends, Request

from application.ports.max_ports import MaxBotPort
from interfaces.deps import get_max_bot

router = APIRouter(prefix="/api/bot", tags=["bot"])


@router.post("/webhook")
async def bot_webhook(
    request: Request,
    max_bot: MaxBotPort = Depends(get_max_bot),
) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return max_bot.handle_webhook(payload if isinstance(payload, dict) else {"raw": payload})
