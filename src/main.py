"""Main FastAPI application module for AceReserve API.

This module sets up the FastAPI application, configures the database lifecycle,
and registers all API routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from .core.async_database import create_db_and_tables, close_db
from .routers import users, courts, reservations, loyalty, coach, favorites, reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application lifecycle.

    Creates database tables on startup and performs cleanup on shutdown.

    Args:
        app: The FastAPI application instance.
    """
    await create_db_and_tables()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    """Root endpoint to verify API is running.

    Returns:
        dict: A welcome message.
    """
    return {"message": "Welcome to AceReserve API!"}


app.include_router(users.router)
app.include_router(courts.router)
app.include_router(reservations.router)
app.include_router(loyalty.router)
app.include_router(coach.router)
app.include_router(favorites.router)
app.include_router(reviews.router)
