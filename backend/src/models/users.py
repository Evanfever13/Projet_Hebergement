from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base

if TYPE_CHECKING:
    from backend.src.models.tickets import Ticket, TicketPermission


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    shared_ticket_permissions: Mapped[list["TicketPermission"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
