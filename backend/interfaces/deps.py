from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Generator, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from application.ports.max_ports import MaxBotPort, MaxBridgePort
from infrastructure.config import Settings, get_settings
from infrastructure.max.max_bot_mock import MaxBotMock
from infrastructure.max.max_bot_real import MaxBotReal
from infrastructure.max.max_bridge_mock import MaxBridgeMock
from infrastructure.max.max_bridge_real import MaxBridgeReal
from infrastructure.persistence.models import make_engine, make_session_factory
from infrastructure.persistence.repositories import (
    SqlBuildingRepository,
    SqlCategoryRepository,
    SqlOrganizationRepository,
    SqlSpecialistRepository,
    SqlTicketRepository,
)

_settings = get_settings()
_engine = make_engine(_settings.database_url)
SessionLocal = make_session_factory(_engine)

_max_bot: MaxBotPort
_max_bridge: MaxBridgePort
if _settings.max_mode.lower() == "real":
    _max_bot = MaxBotReal(_settings.max_bot_token)
    _max_bridge = MaxBridgeReal(_settings.max_bot_token)
else:
    _max_bot = MaxBotMock()
    _max_bridge = MaxBridgeMock()

security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_settings_dep() -> Settings:
    return _settings


def get_max_bot() -> MaxBotPort:
    return _max_bot


def get_max_bridge() -> MaxBridgePort:
    return _max_bridge


def get_engine():
    return _engine


@dataclass
class DispatcherAuth:
    dispatcher_id: str
    organization_id: str
    username: str


def get_current_dispatcher(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> DispatcherAuth:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация диспетчера",
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return DispatcherAuth(
            dispatcher_id=payload["dispatcher_id"],
            organization_id=payload["organization_id"],
            username=payload.get("username", ""),
        )
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )


def optional_dispatcher(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> Optional[DispatcherAuth]:
    if not credentials:
        return None
    try:
        return get_current_dispatcher(credentials, settings)
    except HTTPException:
        return None


def get_resident_ref(
    x_max_user_id: Annotated[Optional[str], Header(alias="X-Max-User-Id")] = None,
) -> str:
    if not x_max_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заголовок X-Max-User-Id обязателен",
        )
    return x_max_user_id


def repos(db: Session):
    return {
        "buildings": SqlBuildingRepository(db),
        "categories": SqlCategoryRepository(db),
        "tickets": SqlTicketRepository(db),
        "specialists": SqlSpecialistRepository(db),
        "organizations": SqlOrganizationRepository(db),
    }
