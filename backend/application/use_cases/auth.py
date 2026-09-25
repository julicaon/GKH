from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from application.ports.organization_repository import OrganizationRepository
from domain.exceptions import AuthenticationError
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


@dataclass
class LoginDispatcher:
    organizations: OrganizationRepository
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 60 * 12

    def execute(self, username: str, password: str) -> dict:
        account = self.organizations.get_dispatcher_by_username(username)
        if not account or not verify_password(password, account.password_hash):
            raise AuthenticationError("Неверный логин или пароль")
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.token_expire_minutes)
        payload = {
            "sub": account.id,
            "dispatcher_id": account.id,
            "organization_id": account.organization_id,
            "username": account.username,
            "exp": expire,
        }
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return {
            "access_token": token,
            "token_type": "bearer",
            "dispatcher_id": account.id,
            "organization_id": account.organization_id,
            "username": account.username,
            "full_name": account.full_name,
        }
