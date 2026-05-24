import os
import shutil

from app.database.connection import SessionLocal
from app.database.models import Breve


def criar_breve(
    nome,
    patente,
    passaporte,
    idade,
    data_conclusao,
    foto
):

    db = SessionLocal()

    pasta_upload = "app/static/uploads"

    os.makedirs(
        pasta_upload,
        exist_ok=True
    )

    caminho_foto = f"{pasta_upload}/{foto.filename}"

    with open(caminho_foto, "wb") as buffer:

        shutil.copyfileobj(
            foto.file,
            buffer
        )

    novo_breve = Breve(

        nome=nome,

        patente=patente,

        passaporte=passaporte,

        idade=idade,

        data_conclusao=data_conclusao,

        foto=foto.filename
    )

    db.add(novo_breve)

    db.commit()

    db.refresh(novo_breve)

    db.close()

    return {
        "success": True,
        "id": novo_breve.id,
        "message": "Breve salvo com sucesso"
    }