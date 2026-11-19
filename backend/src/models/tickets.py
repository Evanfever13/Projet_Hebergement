from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from src.models.users import Users


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    time: Mapped[int] = mapped_column(Integer, nullable=False)
    adopt: Mapped[int] = mapped_column(Integer, nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner: Mapped[Users] = relationship(back_populates="tickets")
    permissions: Mapped[list["TicketPermission"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )


class TicketPermission(Base):
    __tablename__ = "ticket_permissions"
    __table_args__ = (UniqueConstraint("ticket_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    can_edit: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    ticket: Mapped[Ticket] = relationship(back_populates="permissions")
    user: Mapped[Users] = relationship(back_populates="shared_ticket_permissions")
