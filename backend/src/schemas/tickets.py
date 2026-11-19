from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TicketStatus = Literal["Ouvert", "En cours", "Terminé"]


class TicketCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketResponse(TicketCreate):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: int
    status: TicketStatus
    created_at: datetime
