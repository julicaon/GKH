from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from application.use_cases.org import CreateSpecialist, ListSpecialists, UpdateSpecialist
from domain.exceptions import SpecialistNotFoundError, ValidationError
from interfaces.deps import DispatcherAuth, get_current_dispatcher, get_db, repos
from interfaces.schemas import (
    SpecialistIn,
    SpecialistOut,
    SpecialistUpdateIn,
    specialist_out,
)

router = APIRouter(prefix="/api/specialists", tags=["specialists"])


@router.get("", response_model=list[SpecialistOut])
def list_specialists(
    organizationId: Optional[str] = Query(None),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    dispatcher: DispatcherAuth = Depends(get_current_dispatcher),
):
    org_id = organizationId or dispatcher.organization_id
    r = repos(db)
    items = ListSpecialists(specialists=r["specialists"]).execute(
        org_id, active_only=active_only
    )
    return [specialist_out(s) for s in items]


@router.post("", response_model=SpecialistOut)
def create_specialist(
    body: SpecialistIn,
    db: Session = Depends(get_db),
    dispatcher: DispatcherAuth = Depends(get_current_dispatcher),
):
    r = repos(db)
    try:
        s = CreateSpecialist(
            specialists=r["specialists"], organizations=r["organizations"]
        ).execute(
            organization_id=body.organizationId or dispatcher.organization_id,
            full_name=body.fullName,
            skill_tags=body.skillTags,
            active=body.active,
            id=body.id,
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return specialist_out(s)


@router.patch("/{specialist_id}", response_model=SpecialistOut)
def update_specialist(
    specialist_id: str,
    body: SpecialistUpdateIn,
    db: Session = Depends(get_db),
    dispatcher: DispatcherAuth = Depends(get_current_dispatcher),
):
    r = repos(db)
    try:
        s = UpdateSpecialist(specialists=r["specialists"]).execute(
            specialist_id=specialist_id,
            full_name=body.fullName,
            skill_tags=body.skillTags,
            active=body.active,
        )
    except SpecialistNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return specialist_out(s)
