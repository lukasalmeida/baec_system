import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.database import models
from app.database.base import Base
from app.database.connection import SessaoLocal
from app.database.connection import motor
from app.routes.admin import roteador as roteador_admin
from app.routes.api import roteador as roteador_api
from app.routes.auth import roteador as roteador_autenticacao
from app.routes.web import roteador as roteador_web
from app.services.rbac_service import garantir_dados_padrao_rbac

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "baec-dev-secret-key"),
    same_site="lax",
    https_only=False,
)

Base.metadata.create_all(bind=motor)

banco_dados = SessaoLocal()
try:
    garantir_dados_padrao_rbac(banco_dados)
finally:
    banco_dados.close()

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

app.include_router(roteador_web)
app.include_router(roteador_api)
app.include_router(roteador_autenticacao)
app.include_router(roteador_admin)


