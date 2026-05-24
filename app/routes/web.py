from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.session import exigir_permissao_web
from app.database.connection import SessaoLocal
from app.services.breve_service import gerar_codigo_breve
from app.services.rbac_service import PERMISSAO_ADMIN_PERMISSOES
from app.services.rbac_service import PERMISSAO_GERAR_BREVE
from app.services.rbac_service import usuario_tem_permissao

roteador = APIRouter()

modelos_html = Jinja2Templates(directory="app/templates")


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
                "numero": numero,
                "ano": ano,
                "nome_usuario": usuario_autenticado.nome_usuario,
                "pode_gerenciar_permissoes": pode_gerenciar_permissoes,
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





