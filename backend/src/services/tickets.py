from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database import get_db
from src.models.tickets import Ticket
from src.schemas.tickets import TicketCreate, TicketStatusUpdate


def list_tickets(
    db: Session = Depends(get_db),
) -> list[Ticket]:
    return db.query(Ticket).all()


def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable"
        )
    return ticket


def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
) -> Ticket:
    ticket = Ticket(**ticket_data.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_status(
    ticket_id: int,
    ticket_data: TicketStatusUpdate,
    db: Session = Depends(get_db),
) -> Ticket:
    ticket = get_ticket(ticket_id, db)
    ticket.status = ticket_data.status
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> Response:
    ticket = get_ticket(ticket_id, db)
    db.delete(ticket)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
