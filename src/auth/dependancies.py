from fastapi import Depends
from ..models.user import User, Role
from ..core.exceptions import CoachAccessError, AdminAccessError
from .security import get_current_user


def get_current_coach(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.COACH:
        raise CoachAccessError()
    return current_user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.ADMIN:
        raise AdminAccessError()
    return current_user
