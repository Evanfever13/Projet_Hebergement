from datetime import datetime, timedelta, timezone
import os
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from pwdlib import PasswordHash
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.src.models.users import Users as UserModel
from backend.src.schemas.users import UserCreate

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if os.environ.get("VERCEL") == "1" or os.environ.get("RENDER") == "true":
        raise RuntimeError("SECRET_KEY must be configured in production.")
    SECRET_KEY = "local-dev-secret-change-before-deployment"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("motdepassedefolie")

#Données extraites du payload d'un token JWT décodé.
class TokenData(BaseModel):
    username: str | None = None


# Vérifie qu'un mot de passe en clair correspond à son hash.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# Hache un mot de passe en clair avec l'algorithme recommandé (argon2).
def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


# Recherche un utilisateur en base par son nom d'utilisateur.
def get_user(db: Session, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()


# Authentifie un utilisateur, en se protégeant des attaques par timing via un hash factice.
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.password):
        return False
    return user


# Crée un nouvel utilisateur en base avec son mot de passe haché.
def create_user(user: UserCreate, db: Session):
    existing_user = db.query(UserModel).filter(
        or_(UserModel.username == user.username, UserModel.email == str(user.email))
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username ou email déjà utilisé",
        )

    user_dict = user.model_dump()
    plain_password = user_dict.pop("password")
    hashed_password = get_password_hash(plain_password)

    new_user = UserModel(**user_dict, password=hashed_password)
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username ou email déjà utilisé",
        ) from error
    db.refresh(new_user)
    return new_user


# Génère un token JWT signé, valable 15 minutes par défaut.
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Décode le token JWT et retourne l'utilisateur authentifié correspondant.
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# Endpoint d'inscription : crée un nouvel utilisateur.
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(user=user, db=db)


# Endpoint de connexion : authentifie l'utilisateur et délivre un token JWT.
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }