from multiprocessing import context

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database.connection import SessionLocal
from app.services.breve_service import gerar_cog_breve

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@router.get("/gerar-breve", response_class=HTMLResponse)
async def home(request: Request):
    db = SessionLocal()

    try:
        codigo, numero, ano = gerar_cog_breve(db)

        return templates.TemplateResponse(
            name="breve.html",
            request=request,
            context={
                "titulo": "BAEC BREVÊ",
                "codigo": codigo,
                "numero": numero,
                "ano": ano
            }
        )

    finally:
        db.close()