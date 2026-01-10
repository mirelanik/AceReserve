from fastapi import Depends
from ..models.user import User, Role
from .security import get_current_user

ROLE_HIERARCHY = {
    Role.GUEST: 0,
    Role.USER: 1,
    Role.COACH: 2,
    Role.ADMIN: 3,
}


class RoleChecker:
    def __init__(self, required_role: Role):
        self.required_role = required_role

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        user_role_level = ROLE_HIERARCHY.get(current_user.role, 0)
        required_role_level = ROLE_HIERARCHY.get(self.required_role, 0)
        if user_role_level < required_role_level:
            raise PermissionError(
                f"User does not have the required role: {self.required_role}"
            )
        return current_user


require_user = RoleChecker(Role.USER)
require_coach = RoleChecker(Role.COACH)
require_admin = RoleChecker(Role.ADMIN)
