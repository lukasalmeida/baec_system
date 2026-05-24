from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.session import obter_usuario_atual
from app.auth.session import obter_usuario_sessao
from app.database.connection import SessaoLocal
from app.services.auth_service import (
    buscar_usuario_por_nome_usuario,
    criar_usuario,
    validar_senha,
)
from app.services.rbac_service import PERMISSAO_ADMIN_PERMISSOES
from app.services.rbac_service import PERMISSAO_GERAR_BREVE
from app.services.rbac_service import usuario_tem_permissao

roteador = APIRouter()

modelos_html = Jinja2Templates(directory="app/templates")


def renderizar_template_autenticacao(
    request: Request,
    modo: str,
    mensagem_erro: str = "",
    nome_usuario: str = "",
):
    return modelos_html.TemplateResponse(
        name="login.html",
        request=request,
        context={
            "modo": modo,
            "mensagem_erro": mensagem_erro,
            "nome_usuario": nome_usuario,
        },
    )


def obter_redirecionamento_do_usuario(banco_dados, id_usuario: int) -> str:
    if usuario_tem_permissao(banco_dados, id_usuario, PERMISSAO_GERAR_BREVE):
        return "/gerar-breve"

    if usuario_tem_permissao(banco_dados, id_usuario, PERMISSAO_ADMIN_PERMISSOES):
        return "/admin/permissoes"

    return "/acesso-negado"


@roteador.get("/", include_in_schema=False)
async def entrada(request: Request):
    usuario_sessao = obter_usuario_sessao(request)
    if not usuario_sessao:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    usuario = obter_usuario_atual(request)
    if not usuario:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    banco_dados = SessaoLocal()
    try:
        return RedirectResponse(
            url=obter_redirecionamento_do_usuario(banco_dados, usuario.id),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    finally:
        banco_dados.close()


@roteador.get("/login", response_class=HTMLResponse)
async def pagina_login(request: Request):
    usuario = obter_usuario_atual(request)
    if usuario:
        banco_dados = SessaoLocal()
        try:
            return RedirectResponse(
                url=obter_redirecionamento_do_usuario(banco_dados, usuario.id),
                status_code=status.HTTP_303_SEE_OTHER,
            )
        finally:
            banco_dados.close()

    return renderizar_template_autenticacao(request=request, modo="login")


@roteador.post("/login")
async def autenticar(
    request: Request,
    nome_usuario: str = Form(...),
    senha: str = Form(...),
):
    banco_dados = SessaoLocal()

    try:
        usuario = buscar_usuario_por_nome_usuario(banco_dados, nome_usuario.strip())

        if not usuario or not validar_senha(senha, usuario.hash_senha):
            return renderizar_template_autenticacao(
                request=request,
                modo="login",
                mensagem_erro="Usuario ou senha invalidos.",
                nome_usuario=nome_usuario,
            )

        request.session["auth_user"] = {
            "id": usuario.id,
            "nome_usuario": usuario.nome_usuario,
        }

        return RedirectResponse(
            url=obter_redirecionamento_do_usuario(banco_dados, usuario.id),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    finally:
        banco_dados.close()


@roteador.get("/cadastro", response_class=HTMLResponse)
async def pagina_cadastro(request: Request):
    usuario = obter_usuario_atual(request)
    if usuario:
        banco_dados = SessaoLocal()
        try:
            return RedirectResponse(
                url=obter_redirecionamento_do_usuario(banco_dados, usuario.id),
                status_code=status.HTTP_303_SEE_OTHER,
            )
        finally:
            banco_dados.close()

    return renderizar_template_autenticacao(request=request, modo="register")


@roteador.post("/cadastro")
async def cadastrar(
    request: Request,
    nome_usuario: str = Form(...),
    senha: str = Form(...),
):
    nome_usuario = nome_usuario.strip()
    banco_dados = SessaoLocal()

    try:
        if len(nome_usuario) < 3:
            return renderizar_template_autenticacao(
                request=request,
                modo="register",
                mensagem_erro="Usuario deve ter ao menos 3 caracteres.",
                nome_usuario=nome_usuario,
            )

        if len(senha) < 6:
            return renderizar_template_autenticacao(
                request=request,
                modo="register",
                mensagem_erro="Senha deve ter ao menos 6 caracteres.",
                nome_usuario=nome_usuario,
            )

        usuario_existente = buscar_usuario_por_nome_usuario(banco_dados, nome_usuario)
        if usuario_existente:
            return renderizar_template_autenticacao(
                request=request,
                modo="register",
                mensagem_erro="Este usuario ja existe.",
                nome_usuario=nome_usuario,
            )

        usuario_criado = criar_usuario(banco_dados, nome_usuario, senha)
        request.session["auth_user"] = {
            "id": usuario_criado.id,
            "nome_usuario": usuario_criado.nome_usuario,
        }

        return RedirectResponse(
            url=obter_redirecionamento_do_usuario(banco_dados, usuario_criado.id),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    finally:
        banco_dados.close()


@roteador.post("/logout")
async def sair(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)





