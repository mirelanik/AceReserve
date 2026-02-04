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


class DatabaseService:
    def __init__(self, database_url: str | None = None):
        """Initialize async database service.
        Args:
            database_url: SQLAlchemy async database URL. If None, uses config settings.
        """
        url = database_url or self._get_database_url()
        self.engine: AsyncEngine = create_async_engine(url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    @staticmethod
    def _get_database_url() -> str:
        """Get database URL from settings, ensuring async driver.
        Returns:
            str: Async database URL.
        """

        url = getattr(settings, "DATABASE_URL", None)
        if not url:
            return "sqlite+aiosqlite:///:memory:"
        if url.startswith("sqlite://"):
            url = url.replace("sqlite://", "sqlite+aiosqlite:///")
        return url

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session for dependency injection.
        Yields:
            AsyncSession: Database session.
        """
        async with self.async_session() as session:
            yield session

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

    async def create_default_admin(self) -> None:
        """Create a default admin user on first system startup.

        Admin is created ONLY if the database is completely empty (no users exist).
        This ensures secure setup without hardcoded credentials.
        """

        try:
            async with self.async_session() as session:
                try:
                    result = await session.execute(select(User))
                    users = result.scalars().all()
                except Exception:
                    return

                if not users:
                    admin_email = getattr(
                        settings, "FIRST_ADMIN_EMAIL", "admin@example.com"
                    )
                    admin_password = getattr(
                        settings, "FIRST_ADMIN_PASSWORD", "changeme"
                    )

                    if not admin_password:
                        print("Warning: Admin password not set")
                        return

                    admin_user = User(
                        email=admin_email,
                        hashed_password=get_password_hash(admin_password),
                        full_name="Admin",
                        role=Role.ADMIN,
                    )
                    session.add(admin_user)
                    await session.commit()
                    print("Admin user created.")
        except Exception as e:
            print(f"Skipping admin creation due to error: {e}")


db = DatabaseService()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session for FastAPI dependencies.
    Wraps the db instance's get_session method for use as a FastAPI Depends() dependency.
    Yields:
        AsyncSession: Database session for use in dependencies.
    """
    async with db.async_session() as session:
        yield session
