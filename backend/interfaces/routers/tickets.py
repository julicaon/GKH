from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from application.ports.max_ports import MaxBotPort
from application.use_cases.tickets import (
    AcceptTicket,
    AssignSpecialist,
    CancelTicketByResident,
    CompleteTicket,
    GetTicket,
    ListTicketsForOrg,
    ListTicketsForResident,
    SubmitTicket,
)
from domain.exceptions import (
    BuildingNotFoundError,
    CategoryNotFoundError,
    DomainError,
    SpecialistNotFoundError,
    TicketNotFoundError,
    ValidationError,
)
from interfaces.deps import (
    DispatcherAuth,
    get_current_dispatcher,
    get_db,
    get_max_bot,
    optional_dispatcher,
    repos,
)
from interfaces.schemas import AssignIn, SubmitTicketIn, TicketOut, ticket_out

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def _map_error(e: Exception) -> HTTPException:
    if isinstance(e, (TicketNotFoundError, BuildingNotFoundError, CategoryNotFoundError, SpecialistNotFoundError)):
        return HTTPException(status_code=404, detail=str(e))
    if isinstance(e, DomainError):
        return HTTPException(status_code=400, detail=str(e))
    return HTTPException(status_code=500, detail="Внутренняя ошибка")


@router.post("", response_model=TicketOut)
def submit_ticket(
    body: SubmitTicketIn,
    db: Session = Depends(get_db),
    max_bot: MaxBotPort = Depends(get_max_bot),
    x_max_user_id: Annotated[Optional[str], Header(alias="X-Max-User-Id")] = None,
):
    if not x_max_user_id:
        raise HTTPException(status_code=400, detail="Заголовок X-Max-User-Id обязателен")
    r = repos(db)
    try:
        ticket = SubmitTicket(
            buildings=r["buildings"],
            categories=r["categories"],
            tickets=r["tickets"],
            max_bot=max_bot,
        ).execute(
            building_id=body.buildingId,
            category_id=body.categoryId,
            answers=body.answers,
            resident_ref=x_max_user_id,
            photo_url=body.photoUrl,
        )
    except Exception as e:
        raise _map_error(e)
    return ticket_out(ticket)


@router.get("", response_model=list[TicketOut])
def list_tickets(
    role: str = Query(..., description="org|resident"),
    db: Session = Depends(get_db),
    dispatcher: Optional[DispatcherAuth] = Depends(optional_dispatcher),
    x_max_user_id: Annotated[Optional[str], Header(alias="X-Max-User-Id")] = None,
):
    r = repos(db)
    if role == "org":
        if not dispatcher:
            raise HTTPException(status_code=401, detail="Требуется авторизация диспетчера")
        items = ListTicketsForOrg(tickets=r["tickets"]).execute(dispatcher.organization_id)
    elif role == "resident":
        if not x_max_user_id:
            raise HTTPException(status_code=400, detail="Заголовок X-Max-User-Id обязателен")
        items = ListTicketsForResident(tickets=r["tickets"]).execute(x_max_user_id)
    else:
        raise HTTPException(status_code=400, detail="role должен быть org или resident")
    return [ticket_out(t) for t in items]


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    r = repos(db)
    try:
        ticket = GetTicket(tickets=r["tickets"]).execute(ticket_id)
    except TicketNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ticket_out(ticket)


@router.post("/{ticket_id}/accept", response_model=TicketOut)
def accept_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    dispatcher: DispatcherAuth = Depends(get_current_dispatcher),
):
    r = repos(db)
    try:
        ticket = AcceptTicket(tickets=r["tickets"]).execute(
            ticket_id, dispatcher.dispatcher_id
        )
    except Exception as e:
        raise _map_error(e)
    return ticket_out(ticket)


@router.post("/{ticket_id}/assign", response_model=TicketOut)
def assign_ticket(
    ticket_id: str,
    body: AssignIn,
    db: Session = Depends(get_db),
    dispatcher: DispatcherAuth = Depends(get_current_dispatcher),
):
    r = repos(db)
    try:
        ticket = AssignSpecialist(
            tickets=r["tickets"], specialists=r["specialists"]
        ).execute(ticket_id, body.specialistId)
    except Exception as e:
        raise _map_error(e)
    return ticket_out(ticket)


@router.post("/{ticket_id}/complete", response_model=TicketOut)
def complete_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    dispatcher: DispatcherAuth = Depends(get_current_dispatcher),
):
    r = repos(db)
    try:
        ticket = CompleteTicket(tickets=r["tickets"]).execute(ticket_id)
    except Exception as e:
        raise _map_error(e)
    return ticket_out(ticket)


@router.post("/{ticket_id}/cancel", response_model=TicketOut)
def cancel_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    x_max_user_id: Annotated[Optional[str], Header(alias="X-Max-User-Id")] = None,
):
    r = repos(db)
    try:
        ticket = CancelTicketByResident(tickets=r["tickets"]).execute(
            ticket_id, resident_ref=x_max_user_id
        )
    except Exception as e:
        raise _map_error(e)
    return ticket_out(ticket)
