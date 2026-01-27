"""User management service functions.
Handles user creation, authentication, and admin operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from ..models.user import UserCreate, User, Role
from ..core.exceptions import ExistingUserError, UserNotFoundError
from ..auth.hashing import get_password_hash, verify_password
from ..models.loyalty import LoyaltyAccount
from ..models.reservation import Reservation, ReservationStatus


class UserService:
    def __init__(self, session: AsyncSession):
        """Initialize UserService with database session.
        Args:
            session: Async SQLAlchemy database session.
        """
        self.session = session

    async def _create_loyalty_account(self, new_user: User):
        """Create a loyalty account for a new user.
        Args:
            new_user: The newly created user.
        """
        loyalty = LoyaltyAccount(user_id=new_user.id, points=0)

        self.session.add(loyalty)
        await self.session.commit()
        await self.session.refresh(new_user)

    async def create_user(self, user_input: UserCreate) -> User:
        """Create a new user with email and password.
        Args:
            user_input: User registration data.
        Returns:
            User: The newly created user.
        """
        result = await self.session.execute(
            select(User).where(User.email == user_input.email)
        )
        existing_user = result.scalars().first()

        if existing_user:
            raise ExistingUserError()

        hashed_password = get_password_hash(user_input.password)

        new_user = User(
            email=user_input.email,
            hashed_password=hashed_password,
            full_name=user_input.full_name,
            role=Role.USER,
        )

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        await self._create_loyalty_account(new_user)

        return new_user

    async def create_user_by_admin(
        self,
        user_input: UserCreate,
        role: Role,
        user: User
    ) -> User:
        """Create a new user by admin only.
        Args:
            user_input: User registration data.
            role: The role to assign to the new user.
            user: The user performing the operation.
        Returns:
            User: The newly created user with assigned role.
        """
        new_user = await self.create_user(user_input)
        new_user.role = role

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user

    async def remove_user_by_admin(
        self,
        user_id: int,
    ) -> dict:
        """Delete a user and cancel their reservations (admin only).
        Args:
            user_id: ID of the user to delete.
        Returns:
            dict: Success message.
        """
        user = await self.session.get(User, user_id)
        if not user:
            raise UserNotFoundError()

        result = await self.session.execute(
            select(Reservation).where(Reservation.user_id == user_id)
        )
        user_reservations = result.scalars().all()
        for reservation in user_reservations:
            reservation.status = ReservationStatus.CANCELLED
            self.session.add(reservation)

        await self.session.delete(user)
        await self.session.commit()
        return {"msg": "User deleted successfully"}

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user with email and password.
        Args:
            email: The user's email address.
            password: The user's password.
        """
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
