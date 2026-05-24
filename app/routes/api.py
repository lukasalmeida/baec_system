from fastapi import APIRouter
from fastapi import File
from fastapi import Form
from fastapi import Request
from fastapi import UploadFile

from app.auth.session import exigir_permissao_api
from app.services.breve_service import criar_breve
from app.services.rbac_service import PERMISSAO_GERAR_BREVE

roteador = APIRouter(prefix="/api")


@roteador.post("/breve")
async def salvar_breve(
    request: Request,
    nome: str = Form(...),
    patente: str = Form(...),
    passaporte: str = Form(...),
    idade: str = Form(...),
    data_conclusao: str = Form(...),
    foto: UploadFile = File(...),
):
    exigir_permissao_api(request, PERMISSAO_GERAR_BREVE)

    return criar_breve(
        nome,
        patente,
        passaporte,
        idade,
        data_conclusao,
        foto,
    )





