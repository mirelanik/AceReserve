"""Role-based access control for API endpoints.
Defines role hierarchy and provides role-checking dependency injectors.
"""

from fastapi import Depends
from ..models.user import User, Role
from .security import get_current_user
from fastapi import HTTPException, status

ROLE_HIERARCHY = {
    Role.GUEST: 0,
    Role.USER: 1,
    Role.COACH: 2,
    Role.ADMIN: 3,
}


class RoleChecker:
    """Dependency for checking user roles in API endpoints."""

    def __init__(self, required_role: Role):
        """Initialize with required role.
        Args:
            required_role: The minimum role required to access the endpoint.
        """
        self.required_role = required_role

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """Check if user has required role.
        Args:
            current_user: The authenticated user.
        Returns:
            User: The user if they have sufficient permissions.
        """
        user_role_level = ROLE_HIERARCHY.get(current_user.role, 0)
        required_role_level = ROLE_HIERARCHY.get(self.required_role, 0)
        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required privileges."
            )
        return current_user


require_user = RoleChecker(Role.USER)
require_coach = RoleChecker(Role.COACH)
require_admin = RoleChecker(Role.ADMIN)
