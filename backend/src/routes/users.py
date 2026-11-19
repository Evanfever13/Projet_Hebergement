from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from src.models.users import Users
from src.schemas.users import Token, UserCreate, UserResponse
from src.services.users import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte utilisateur",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> Users:
    return create_user(user_data, db)


@router.post(
    "/login",
    response_model=Token,
    summary="Se connecter et recevoir un jeton JWT",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token(user.id))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Récupérer le compte connecté",
)
def read_current_user(
    current_user: Users = Depends(get_current_user),
) -> Users:
    return current_user
