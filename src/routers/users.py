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


@router.post("/register", response_model=UserRead)
async def register_user(
    user_input: UserCreate, service: UserService = Depends(get_user_service)
):
    """Register a new user with email and password.
    Args:
        user_input: User registration data.
        service: UserService instance.
    Returns:
        UserRead: The newly registered user information.
    """
    return await service.create_user(user_input)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: UserService = Depends(get_user_service),
):
    """Authenticate user and get JWT access token.
    Args:
        form_data: OAuth2 form with username (email) and password.
        service: UserService instance.
    Returns:
        dict: Contains 'access_token' and 'token_type'.
    """
    user_authenticated = await service.authenticate_user(
        email=form_data.username, password=form_data.password
    )

    if not user_authenticated:
        raise UnauthorizedUserError()

    access_token = create_access_token(data={"sub": str(user_authenticated.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def show_current_user(current_user: UserRead = Depends(require_user)):
    """Get the current authenticated user's information.
    Args:
        current_user: The authenticated user (injected from token).
    Returns:
        UserRead: The current user's information.
    """
    return current_user


@router.post("/create-by-admin", response_model=UserRead)
async def add_user_by_admin(
    user_input: UserCreate,
    role: Role = Role.USER,
    current_user: User = Depends(require_admin),
    service: UserService = Depends(get_user_service),
):
    """Create a new user with a specific role (admin only).
    Args:
        user_input: User creation data.
        role: Role to assign to the user.
        current_user: The authenticated admin user.
        service: UserService instance.
    Returns:
        UserRead: The newly created user.
    """
    return await service.create_user_by_admin(user_input, role, current_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    service: UserService = Depends(get_user_service),
):
    """Delete a user and cancel their reservations (admin only).
    Args:
        user_id: ID of the user to delete.
        current_user: The authenticated admin user.
        service: UserService instance.
    Returns:
        dict: Success message.
    """
    return await service.remove_user_by_admin(user_id)
