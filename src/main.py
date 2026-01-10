from contextlib import asynccontextmanager
from fastapi import FastAPI
from .core.database import create_db_and_tables
from .routers import users, courts, reservations, loyalty, coach, favorites, reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Welcome to AceReserve API!"}


app.include_router(users.router)
app.include_router(courts.router)
app.include_router(reservations.router)
app.include_router(loyalty.router)
app.include_router(coach.router)
app.include_router(favorites.router)
app.include_router(reviews.router)
