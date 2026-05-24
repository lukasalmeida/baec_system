from fastapi import HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.database.connection import SessaoLocal
from app.database.models import Usuario
from app.services.rbac_service import usuario_tem_permissao


def obter_usuario_sessao(request: Request):
    usuario = request.session.get("auth_user")

    if not isinstance(usuario, dict):
        return None

    id_usuario = usuario.get("id")
    nome_usuario = usuario.get("nome_usuario")

    if id_usuario is None or not nome_usuario:
        return None

    return usuario


def obter_usuario_atual(request: Request):
    usuario_sessao = obter_usuario_sessao(request)

    if not usuario_sessao:
        return None

    banco_dados = SessaoLocal()

    try:
        return banco_dados.query(Usuario).filter(Usuario.id == usuario_sessao["id"]).first()
    finally:
        banco_dados.close()


def exigir_autenticacao_web(request: Request):
    usuario = obter_usuario_atual(request)

    if usuario:
        return usuario

    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


def exigir_autenticacao_api(request: Request):
    usuario = obter_usuario_atual(request)

    if usuario:
        return usuario

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuario nao autenticado"
    )


def exigir_permissao_web(request: Request, codigo_permissao: str):
    usuario = exigir_autenticacao_web(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    banco_dados = SessaoLocal()

    try:
        if usuario_tem_permissao(banco_dados, usuario.id, codigo_permissao):
            return usuario
    finally:
        banco_dados.close()

    return RedirectResponse(
        url="/acesso-negado",
        status_code=status.HTTP_303_SEE_OTHER
    )


def exigir_permissao_api(request: Request, codigo_permissao: str):
    usuario = exigir_autenticacao_api(request)

    banco_dados = SessaoLocal()

    try:
        if usuario_tem_permissao(banco_dados, usuario.id, codigo_permissao):
            return usuario
    finally:
        banco_dados.close()

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Sem permissao para executar esta operacao"
    )


