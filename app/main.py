from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.web import router as web_router
from app.routes.api import router as api_router

from app.database.connection import engine
from app.database.base import Base

from app.database import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

app.include_router(web_router)
app.include_router(api_router)

