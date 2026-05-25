import os
import shutil
from datetime import datetime

from sqlalchemy import func

from app.database.connection import SessaoLocal
from app.database.models import Breve

PREFIXO_CODIGO_BREVE = "BAEC"


def normalizar_codigo_breve(codigo: str) -> str:
    codigo_normalizado = (codigo or "").strip().upper().replace(" ", "")

    if codigo_normalizado.startswith(f"{PREFIXO_CODIGO_BREVE}-"):
        return codigo_normalizado[len(PREFIXO_CODIGO_BREVE) + 1 :]

    return codigo_normalizado


def montar_codigo_breve(codigo_base: str) -> str:
    if not codigo_base:
        return ""

    codigo_normalizado = codigo_base.strip().upper()
    if codigo_normalizado.startswith(f"{PREFIXO_CODIGO_BREVE}-"):
        return codigo_normalizado

    return f"{PREFIXO_CODIGO_BREVE}-{codigo_normalizado}"


def gerar_codigo_breve(banco_dados):
    ano = datetime.now().strftime("%y")

    ultimo_numero = (
        banco_dados.query(func.max(Breve.numero_sequencial))
        .filter(Breve.ano == int(ano))
        .scalar()
    )

    if ultimo_numero is None:
        novo_numero = 1
    else:
        novo_numero = ultimo_numero + 1

    numero_formatado = str(novo_numero).zfill(3)
    codigo = montar_codigo_breve(f"{ano}-{numero_formatado}")

    return codigo, novo_numero, int(ano)


def buscar_breve_por_codigo(banco_dados, codigo: str):
    codigo_base = normalizar_codigo_breve(codigo)
    if not codigo_base:
        return None

    codigo_com_prefixo = montar_codigo_breve(codigo_base)

    return (
        banco_dados.query(Breve)
        .filter(Breve.codigo.in_([codigo_base, codigo_com_prefixo]))
        .order_by(Breve.id.desc())
        .first()
    )


def criar_breve(
    nome,
    patente,
    passaporte,
    idade,
    data_conclusao,
    foto,
):
    banco_dados = SessaoLocal()

    try:
        pasta_upload = "app/static/uploads"
        os.makedirs(pasta_upload, exist_ok=True)

        caminho_foto = f"{pasta_upload}/{foto.filename}"

        with open(caminho_foto, "wb") as arquivo_buffer:
            shutil.copyfileobj(foto.file, arquivo_buffer)

        codigo, numero, ano = gerar_codigo_breve(banco_dados)

        breve = Breve(
            codigo=codigo,
            ano=ano,
            numero_sequencial=numero,
            nome=nome,
            patente=patente,
            passaporte=passaporte,
            idade=idade,
            data_conclusao=data_conclusao,
            foto=foto.filename,
        )

        banco_dados.add(breve)
        banco_dados.commit()
        banco_dados.refresh(breve)

        return {
            "sucesso": True,
            "id": breve.id,
            "codigo": codigo,
            "mensagem": "Breve salvo com sucesso",
        }
    finally:
        banco_dados.close()

