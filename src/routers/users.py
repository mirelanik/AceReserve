from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Annotated
from ..models.user import User, UserCreate, UserRead
from ..services.user_service import create_user, authenticate_user
from ..database import get_session
from ..core.exceptions import UnauthorizedUserError
from ..auth.security import create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=User)
def register_user(user_input: UserCreate, session: Session = Depends(get_session)):
    return create_user(session, user_input)

@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session:Session = Depends(get_session)):
    user_authenticated = authenticate_user(session, email=form_data.username, password=form_data.password)
    
    if not user_authenticated:
        raise UnauthorizedUserError()

    access_token = create_access_token(data={"sub": str(user_authenticated.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
def show_current_user(current_user: UserRead = Depends(get_current_user)):
    return current_user