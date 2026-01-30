"""User management API endpoints.
Handles user registration, login, profile retrieval, and admin user operations.
"""

from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..models.user import UserCreate, UserRead, User, Role
from ..services.user_service import UserService
from ..core.dependencies_services import get_user_service
from ..core.exceptions import UnauthorizedUserError
from ..auth.security import create_access_token
from ..auth.dependencies import require_user, require_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register_user(
    user_input: UserCreate, service: UserService = Depends(get_user_service)
):
    return await service.create_user(user_input)


@router.post("/login", status_code=200)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: UserService = Depends(get_user_service),
):
    user_authenticated = await service.authenticate_user(
        email=form_data.username, password=form_data.password
    )

    if not user_authenticated:
        raise UnauthorizedUserError()

    access_token = create_access_token(data={"sub": str(user_authenticated.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead, status_code=200)
async def show_current_user(current_user: UserRead = Depends(require_user)):
    return current_user


@router.post("/create-by-admin", response_model=UserRead, status_code=201)
async def add_user_by_admin(
    user_input: UserCreate,
    role: Role = Role.USER,
    current_user: User = Depends(require_admin),
    service: UserService = Depends(get_user_service),
):
    return await service.create_user_by_admin(user_input, role, current_user)


@router.delete("/{user_id}", status_code=200)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    service: UserService = Depends(get_user_service),
):
    return await service.remove_user_by_admin(user_id)
