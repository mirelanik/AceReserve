from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import users, courts 

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(courts.router)
