from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database import get_db
from src.models.tickets import Ticket, TicketPermission
from src.models.users import Users
from src.schemas.tickets import TicketCreate
from src.services.users import get_current_user


def list_tickets(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
) -> list[Ticket]:
    return db.query(Ticket).filter(Ticket.owner_id == current_user.id).all()


def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable"
        )

    if ticket.owner_id != current_user.id:
        permission = (
            db.query(TicketPermission)
            .filter(
                TicketPermission.ticket_id == ticket.id,
                TicketPermission.user_id == current_user.id,
            )
            .first()
        )
        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Accès interdit"
            )
    return ticket


def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
) -> Ticket:
    ticket = Ticket(**ticket_data.model_dump(), owner_id=current_user.id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket(
    ticket_id: int,
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
) -> Ticket:
    ticket = get_ticket(ticket_id, db, current_user)
    if ticket.owner_id != current_user.id:
        permission = (
            db.query(TicketPermission)
            .filter(
                TicketPermission.ticket_id == ticket.id,
                TicketPermission.user_id == current_user.id,
                TicketPermission.can_edit.is_(True),
            )
            .first()
        )
        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Modification non autorisée",
            )

    for key, value in ticket_data.model_dump().items():
        setattr(ticket, key, value)
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
) -> Response:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable"
        )
    if ticket.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le propriétaire peut supprimer ce ticket",
        )

    db.delete(ticket)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
