import os
import shutil
from datetime import datetime
from sqlalchemy import func

from app.database.connection import SessionLocal
from app.database.models import Breve


def gerar_cog_breve(db):
    ano = datetime.now().strftime("%y")

    ultimo = (db.query(func.max(Breve.numero_sequencial)).filter(Breve.ano == int(ano)).scalar())

    if ultimo is None:
        novo_numero = 1
    else:
        novo_numero = ultimo + 1

    numero_formatado = str(novo_numero).zfill(3)

    codigo = f"{ano}-{numero_formatado}"

    return codigo, novo_numero, int(ano)


def criar_breve(
        nome,
        patente,
        passaporte,
        idade,
        data_conclusao,
        foto
):
    db = SessionLocal()

    try:
        pasta_upload = "app/static/uploads"
        os.makedirs(pasta_upload, exist_ok=True)

        caminho_foto = f"{pasta_upload}/{foto.filename}"

        with open(caminho_foto, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)

        # 🔥 gera BAEC aqui
        codigo, numero, ano = gerar_cog_breve(db)

        novo_breve = Breve(
            codigo=codigo,
            ano=ano,
            numero_sequencial=numero,

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

        return {
            "success": True,
            "id": novo_breve.id,
            "codigo": codigo,
            "message": "Breve salvo com sucesso"
        }

    finally:
        db.close()
