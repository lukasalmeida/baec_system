from datetime import datetime
from urllib.parse import quote_plus

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.session import exigir_permissao_web
from app.database.connection import SessaoLocal
from app.services.breve_service import buscar_breve_por_codigo
from app.services.breve_service import gerar_codigo_breve
from app.services.breve_service import montar_codigo_breve
from app.services.breve_service import normalizar_codigo_breve
from app.services.rbac_service import PERMISSAO_ADMIN_PERMISSOES
from app.services.rbac_service import PERMISSAO_GERAR_BREVE
from app.services.rbac_service import usuario_tem_permissao

roteador = APIRouter()

modelos_html = Jinja2Templates(directory="app/templates")


def formatar_data_visualizacao(valor_data: str) -> str:
    try:
        return datetime.strptime(valor_data, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return valor_data or ""


@roteador.get("/gerar-breve", response_class=HTMLResponse)
async def pagina_gerar_breve(request: Request):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_GERAR_BREVE)

    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    banco_dados = SessaoLocal()

    try:
        codigo, numero, ano = gerar_codigo_breve(banco_dados)
        pode_gerenciar_permissoes = usuario_tem_permissao(
            banco_dados,
            usuario_autenticado.id,
            PERMISSAO_ADMIN_PERMISSOES,
        )

        return modelos_html.TemplateResponse(
            name="breve.html",
            request=request,
            context={
                "titulo": "BAEC BREVES",
                "codigo": codigo,
                "codigo_exibicao": normalizar_codigo_breve(codigo),
                "numero": numero,
                "ano": ano,
                "nome_usuario": usuario_autenticado.nome_usuario,
                "pode_gerenciar_permissoes": pode_gerenciar_permissoes,
            },
        )
    finally:
        banco_dados.close()


@roteador.get("/consultar-breve", response_class=HTMLResponse)
async def pagina_consultar_breve(
    request: Request,
    erro: str = "",
    codigo: str = "",
):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_GERAR_BREVE)

    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    banco_dados = SessaoLocal()

    try:
        pode_gerenciar_permissoes = usuario_tem_permissao(
            banco_dados,
            usuario_autenticado.id,
            PERMISSAO_ADMIN_PERMISSOES,
        )

        return modelos_html.TemplateResponse(
            name="consulta_breve.html",
            request=request,
            context={
                "titulo": "Consultar breve",
                "nome_usuario": usuario_autenticado.nome_usuario,
                "pode_gerenciar_permissoes": pode_gerenciar_permissoes,
                "erro_consulta": erro,
                "codigo_informado": codigo,
            },
        )
    finally:
        banco_dados.close()


@roteador.post("/consultar-breve")
async def consultar_breve(
    codigo: str = Form(...),
):
    codigo_base = normalizar_codigo_breve(codigo)
    if not codigo_base:
        return RedirectResponse(
            url="/consultar-breve?erro=Informe+um+codigo+valido.",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return RedirectResponse(
        url=f"/ver-breve/{montar_codigo_breve(codigo_base)}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@roteador.get("/ver-breve/{codigo}", response_class=HTMLResponse)
async def pagina_ver_breve(request: Request, codigo: str):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_GERAR_BREVE)

    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    banco_dados = SessaoLocal()

    try:
        breve = buscar_breve_por_codigo(banco_dados, codigo)
        if not breve:
            codigo_informado = quote_plus(montar_codigo_breve(normalizar_codigo_breve(codigo)))
            return RedirectResponse(
                url=(
                    "/consultar-breve"
                    "?erro=Breve+nao+encontrado+para+o+codigo+informado."
                    f"&codigo={codigo_informado}"
                ),
                status_code=status.HTTP_303_SEE_OTHER,
            )

        pode_gerenciar_permissoes = usuario_tem_permissao(
            banco_dados,
            usuario_autenticado.id,
            PERMISSAO_ADMIN_PERMISSOES,
        )

        return modelos_html.TemplateResponse(
            name="ver_breve.html",
            request=request,
            context={
                "titulo": f"Breve {normalizar_codigo_breve(breve.codigo)}",
                "nome_usuario": usuario_autenticado.nome_usuario,
                "pode_gerenciar_permissoes": pode_gerenciar_permissoes,
                "codigo": montar_codigo_breve(breve.codigo),
                "codigo_exibicao": normalizar_codigo_breve(breve.codigo),
                "nome": breve.nome,
                "patente": breve.patente,
                "passaporte": breve.passaporte,
                "idade": breve.idade,
                "data_conclusao": breve.data_conclusao,
                "data_conclusao_formatada": formatar_data_visualizacao(breve.data_conclusao),
                "foto_url": f"/static/uploads/{breve.foto}" if breve.foto else "",
            },
        )
    finally:
        banco_dados.close()


@roteador.get("/acesso-negado", response_class=HTMLResponse)
async def pagina_acesso_negado(request: Request):
    return modelos_html.TemplateResponse(
        name="access_denied.html",
        request=request,
        context={},
    )



