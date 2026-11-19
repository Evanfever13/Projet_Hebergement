from datetime import datetime, timedelta, timezone
import os
import secrets
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from src.models.users import Users
from src.schemas.users import UserCreate

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def _get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")
    if secret_key:
        if len(secret_key.encode("utf-8")) < 32:
            raise RuntimeError("SECRET_KEY doit contenir au moins 32 octets.")
        return secret_key
    if os.getenv("RENDER") == "true" or os.getenv("VERCEL") == "1":
        raise RuntimeError("La variable SECRET_KEY doit être configurée en production.")
    return secrets.token_urlsafe(32)


SECRET_KEY = _get_secret_key()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
password_hash = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hash.hash(secrets.token_urlsafe(32))


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_user(user_data: UserCreate, db: Session) -> Users:
    existing_user = (
        db.query(Users)
        .filter(or_(Users.username == user_data.username, Users.email == str(user_data.email)))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nom d'utilisateur ou adresse e-mail déjà utilisé.",
        )

    user = Users(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=get_password_hash(user_data.password),
        role="user",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nom d'utilisateur ou adresse e-mail déjà utilisé.",
        ) from error
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Users | None:
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        verify_password(password, DUMMY_PASSWORD_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton manquant, invalide ou expiré.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise credentials_exception
        user_id = int(subject)
    except (InvalidTokenError, ValueError):
        raise credentials_exception

    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(
    current_user: Annotated[Users, Depends(get_current_user)],
) -> Users:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette action est réservée aux administrateurs.",
        )
    return current_user


def ensure_admin_user(db: Session) -> Users | None:
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    configured_values = (username, email, password)

    if not any(configured_values):
        if os.getenv("RENDER") == "true":
            raise RuntimeError(
                "ADMIN_USERNAME, ADMIN_EMAIL et ADMIN_PASSWORD doivent être configurés."
            )
        return None
    if not all(configured_values):
        raise RuntimeError(
            "ADMIN_USERNAME, ADMIN_EMAIL et ADMIN_PASSWORD doivent tous être configurés."
        )

    admin_data = UserCreate.model_validate(
        {"username": username, "email": email, "password": password}
    )
    existing_user = (
        db.query(Users)
        .filter(
            or_(
                Users.username == admin_data.username,
                Users.email == str(admin_data.email),
            )
        )
        .first()
    )
    if existing_user:
        if (
            existing_user.username != admin_data.username
            or existing_user.email.lower() != str(admin_data.email).lower()
        ):
            raise RuntimeError(
                "Les identifiants admin configurés correspondent à deux comptes différents."
            )
        if existing_user.role != "admin":
            existing_user.role = "admin"
            existing_user.hashed_password = get_password_hash(admin_data.password)
            db.commit()
        return existing_user

    admin = Users(
        username=admin_data.username,
        email=str(admin_data.email),
        hashed_password=get_password_hash(admin_data.password),
        role="admin",
    )
    db.add(admin)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise RuntimeError(
            "Impossible de créer le compte administrateur initial."
        ) from error
    db.refresh(admin)
    return admin
