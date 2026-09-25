from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from application.use_cases.auth import LoginDispatcher
from domain.exceptions import AuthenticationError
from fastapi import HTTPException
from interfaces.deps import get_db, get_settings_dep, repos
from infrastructure.config import Settings
from interfaces.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db), settings: Settings = Depends(get_settings_dep)):
    r = repos(db)
    uc = LoginDispatcher(
        organizations=r["organizations"],
        jwt_secret=settings.jwt_secret,
        jwt_algorithm=settings.jwt_algorithm,
    )
    try:
        result = uc.execute(body.username, body.password)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return LoginResponse(**result)
