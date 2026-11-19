from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    time: int = Field(ge=0)
    adopt: int = Field(ge=0)


class TicketResponse(TicketCreate):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: int
