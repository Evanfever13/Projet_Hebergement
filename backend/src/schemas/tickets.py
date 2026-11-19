from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)


class TicketResponse(TicketCreate):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: int
    status: Literal["Ouvert", "En cours", "Résolu"]
    created_at: datetime


class TicketStatusUpdate(BaseModel):
    status: Literal["Ouvert", "En cours", "Résolu"]
