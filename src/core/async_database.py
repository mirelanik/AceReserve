"""Asynchronous database service and session management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlmodel import SQLModel, select
from ..core.config import settings
from ..models.user import User, Role
from ..auth.hashing import get_password_hash


DATABASE_URL = getattr(settings, "DATABASE_URL", "sqlite+aiosqlite:///./acereserve.db")

if DATABASE_URL.startswith("sqlite://"):
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite:///")
elif not DATABASE_URL.startswith("sqlite+aiosqlite://"):
    pass

_engine = create_async_engine(DATABASE_URL, echo=False)
_async_session = async_sessionmaker(
    _engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session for FastAPI dependencies."""
    async with _async_session() as session:
        yield session


async def create_default_admin() -> None:
    """Create a default admin user on first system startup.

    Admin is created ONLY if the database is completely empty (no users exist).
    This ensures secure setup without hardcoded credentials.
    """
    
    async with _async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        if not users:
            admin_email = getattr(
                settings, "FIRST_ADMIN_EMAIL"
            )
            admin_password = getattr(settings, "FIRST_ADMIN_PASSWORD")

            if not admin_password:
                print(
                    "Warning: Admin password not set in environment variables"
                )
                return

            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                full_name="Admin",
                role=Role.ADMIN,
            )
            session.add(admin_user)
            await session.commit()
            print(f"Admin user created.")


async def create_db_and_tables() -> None:
    """Create all database tables from SQLModel metadata.

    Should be called during application startup.
    """
    async with _engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    await create_default_admin()


async def close_db() -> None:
    """Close database connection.

    Should be called during application shutdown.
    """
    await _engine.dispose()


class DatabaseService:
    """Async database manager using SQLModel/SQLAlchemy async engine.

    Provides an alternative way to manage database connections.
    """

    def __init__(self, database_url: str | None = None):
        """Initialize async database service.

        Args:
            database_url: SQLAlchemy async database URL. If None, uses config settings.
        """
        url = database_url or DATABASE_URL
        self.engine: AsyncEngine = create_async_engine(url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self) -> None:
        """Create all database tables from SQLModel metadata."""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop all database tables from SQLModel metadata."""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

    async def close(self) -> None:
        """Close database connection."""
        await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        async with self.async_session() as session:
            yield session
