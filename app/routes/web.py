from multiprocessing import context

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@router.get("/gerar-breve", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        name="breve.html",
        request=request,
        context={
            'titulo': "BAEC BREVÊ"
        }
    )