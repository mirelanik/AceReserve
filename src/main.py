from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import users, courts, reservations
from src.models.review import Review


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
