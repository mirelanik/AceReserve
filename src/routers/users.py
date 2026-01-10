from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Annotated
from ..models.user import User, UserCreate, UserRead, Role
from ..services.user_service import (
    create_user,
    authenticate_user,
    create_user_by_admin,
    remove_user_by_admin,
)
from ..core.database import get_session
from ..core.exceptions import UnauthorizedUserError
from ..auth.security import create_access_token
from ..auth.dependencies import require_user, require_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserRead)
def register_user(user_input: UserCreate, session: Session = Depends(get_session)):
    return create_user(session, user_input)


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
):
    user_authenticated = authenticate_user(
        session, email=form_data.username, password=form_data.password
    )

    if not user_authenticated:
        raise UnauthorizedUserError()

    access_token = create_access_token(data={"sub": str(user_authenticated.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def show_current_user(current_user: UserRead = Depends(require_user)):
    return current_user


@router.post("/create-by-admin", response_model=UserRead)
def add_user_by_admin(
    user_input: UserCreate,
    role: Role = Role.USER,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return create_user_by_admin(user_input, role, current_user, session)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    return remove_user_by_admin(user_id, current_user, session)
