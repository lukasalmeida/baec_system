from fastapi import (
    APIRouter,
    Form,
    File,
    UploadFile
)

from app.services.breve_service import criar_breve

router = APIRouter(
    prefix="/api",
)


@router.post("/breve")
async def salvar_breve(

    nome: str = Form(...),

    patente: str = Form(...),

    passaporte: str = Form(...),

    idade: str = Form(...),

    data_conclusao: str = Form(...),

    foto: UploadFile = File(...)

):

    return criar_breve(
        nome,
        patente,
        passaporte,
        idade,
        data_conclusao,
        foto
    )