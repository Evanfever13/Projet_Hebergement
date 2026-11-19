from fastapi import APIRouter, Depends, status

from backend.src.models.users import Users
from backend.src.schemas.users import UserResponse
from backend.src.services.users import get_current_user, login, register
from backend.src.schemas.users import Token

# on initialise nos routes
router2 = APIRouter(prefix="/api/auth", tags=["Users"])
users_router = APIRouter(prefix="/api/users", tags=["Users"])

@users_router.get("/me", response_model=UserResponse)
def read_current_user(current_user: Users = Depends(get_current_user)):
    return current_user

router2.add_api_route(
    "/register",
    endpoint=register,
    methods=["POST"],
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouvel utilisateur",
)

router2.add_api_route(
    "/login",
    endpoint=login,
    methods=["POST"],
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Authentifier un utilisateur et récupérer un jeton JWT",
)