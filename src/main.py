"""Main FastAPI application module for AceReserve API.

This module sets up the FastAPI application, configures the database lifecycle,
and registers all API routers.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .core.async_database import db
from .routers import users, courts, reservations, loyalty, coach, favorites, reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application lifecycle.

    Creates database tables on startup and performs cleanup on shutdown.

    Args:
        app: The FastAPI application instance.
    """

    await db.create_tables()
    if os.getenv("PYTEST_CURRENT_TEST") is None:
        await db.create_default_admin()
    try:
        yield
    finally:
        await db.close()


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
