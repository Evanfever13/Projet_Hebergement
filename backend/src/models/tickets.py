from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

try:
    from database import Base
except ModuleNotFoundError:
    from backend.database import Base


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint(
            "status IN ('Ouvert', 'En cours', 'Résolu')",
            name="tickets_status_check",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Ouvert")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
