"""JWT token creation and validation module.
This module handles OAuth2 JWT token creation, validation, and user authentication
for the AceReserve API.
"""

from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.config import settings
from ..core.exceptions import CredentialsError
from ..core.async_database import db
from ..models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def create_access_token(data: dict) -> str:
    """Create a JWT access token with expiration.
    Args:
        data: Dictionary containing token claims (e.g., user ID).
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db.get_async_session),
) -> User:
    """Get the current authenticated user from JWT token.
    Args:
        token: JWT token.
        session: Async database session.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise CredentialsError()
    except ExpiredSignatureError:
        raise CredentialsError(detail="Token has expired.")
    except InvalidTokenError:
        raise CredentialsError(detail="Invalid token.")

    user = await session.get(User, int(user_id))
    if user is None:
        raise CredentialsError()

    return user
