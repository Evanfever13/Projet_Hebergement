from pydantic import BaseModel, ConfigDict, EmailStr, Field

#Schema pour notre serveur

class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
        
class Token(BaseModel):
    access_token: str
    token_type: str