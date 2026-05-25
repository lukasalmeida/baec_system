from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.session import exigir_permissao_web
from app.database.connection import SessaoLocal
from app.database.models import GrupoPermissao
from app.database.models import Permissao
from app.database.models import Usuario
from app.services.auth_service import criar_usuario
from app.services.auth_service import gerar_hash_senha
from app.services.rbac_service import GRUPO_ADMIN
from app.services.rbac_service import PERMISSAO_ADMIN_PERMISSOES
from app.services.rbac_service import garantir_dados_padrao_rbac

roteador = APIRouter()
modelos_html = Jinja2Templates(directory="app/templates")


def montar_contexto_admin_permissoes(banco_dados, mensagem: str = "", erro: str = ""):
    usuarios = banco_dados.query(Usuario).order_by(Usuario.nome_usuario.asc()).all()
    permissoes = banco_dados.query(Permissao).order_by(Permissao.codigo.asc()).all()
    grupos = banco_dados.query(GrupoPermissao).order_by(GrupoPermissao.nome.asc()).all()

    return {
        "usuarios": usuarios,
        "permissoes": permissoes,
        "grupos": grupos,
        "mensagem": mensagem,
        "erro": erro,
    }


def montar_contexto_admin_usuarios(banco_dados, mensagem: str = "", erro: str = ""):
    usuarios = banco_dados.query(Usuario).order_by(Usuario.nome_usuario.asc()).all()
    grupos = banco_dados.query(GrupoPermissao).order_by(GrupoPermissao.nome.asc()).all()

    return {
        "usuarios": usuarios,
        "grupos": grupos,
        "mensagem": mensagem,
        "erro": erro,
    }


def usuario_eh_admin(usuario: Usuario):
    return any(grupo.nome == GRUPO_ADMIN for grupo in usuario.grupos)


def contar_usuarios_admin(usuarios: list[Usuario]):
    return sum(1 for usuario in usuarios if usuario_eh_admin(usuario))


def carregar_grupo_por_id(banco_dados, id_grupo: str):
    if not id_grupo or not id_grupo.isdigit():
        return None

    return banco_dados.query(GrupoPermissao).filter(GrupoPermissao.id == int(id_grupo)).first()


@roteador.get("/admin/permissoes", response_class=HTMLResponse)
async def pagina_admin_permissoes(request: Request):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_ADMIN_PERMISSOES)

    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    banco_dados = SessaoLocal()
    try:
        garantir_dados_padrao_rbac(banco_dados)
        contexto = montar_contexto_admin_permissoes(banco_dados)
        contexto["nome_usuario"] = usuario_autenticado.nome_usuario

        return modelos_html.TemplateResponse(
            name="admin_permissions.html",
            request=request,
            context=contexto,
        )
    finally:
        banco_dados.close()


@roteador.post("/admin/permissoes/permission/create")
async def criar_permissao(
    request: Request,
    codigo: str = Form(...),
    nome: str = Form(...),
    descricao: str = Form(""),
):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_ADMIN_PERMISSOES)
    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    codigo = codigo.strip().lower()
    nome = nome.strip()

    banco_dados = SessaoLocal()
    try:
        permissao_existente = banco_dados.query(Permissao).filter(Permissao.codigo == codigo).first()
        if permissao_existente:
            return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, erro="Codigo de permissao ja existe.")

        permissao = Permissao(codigo=codigo, nome=nome, descricao=descricao.strip())
        banco_dados.add(permissao)
        banco_dados.commit()

        return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, mensagem="Permissao criada com sucesso.")
    finally:
        banco_dados.close()


@roteador.post("/admin/permissoes/permission/update/{id_permissao}")
async def atualizar_permissao(
    request: Request,
    id_permissao: int,
    codigo: str = Form(...),
    nome: str = Form(...),
    descricao: str = Form(""),
):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_ADMIN_PERMISSOES)
    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    banco_dados = SessaoLocal()
    try:
        permissao = banco_dados.query(Permissao).filter(Permissao.id == id_permissao).first()
        if not permissao:
            return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, erro="Permissao nao encontrada.")

        codigo = codigo.strip().lower()
        permissao_duplicada = (
            banco_dados.query(Permissao)
            .filter(Permissao.codigo == codigo, Permissao.id != id_permissao)
            .first()
        )
        if permissao_duplicada:
            return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, erro="Codigo de permissao ja esta em uso.")

        permissao.codigo = codigo
        permissao.nome = nome
        permissao.descricao = descricao.strip()
        banco_dados.commit()

        return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, mensagem="Permissao atualizada.")
    finally:
        banco_dados.close()


@roteador.post("/admin/permissoes/group/create")
async def criar_grupo(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(""),
):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_ADMIN_PERMISSOES)
    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    nome = nome.strip()

    banco_dados = SessaoLocal()
    try:
        grupo_existente = banco_dados.query(GrupoPermissao).filter(GrupoPermissao.nome == nome).first()
        if grupo_existente:
            return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, erro="Grupo ja existe.")

        grupo = GrupoPermissao(nome=nome, descricao=descricao.strip())
        banco_dados.add(grupo)
        banco_dados.commit()

        return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, mensagem="Grupo criado com sucesso.")
    finally:
        banco_dados.close()


@roteador.post("/admin/permissoes/group/update/{id_grupo}")
async def atualizar_grupo(
    request: Request,
    id_grupo: int,
    descricao: str = Form(""),
    ids_permissoes: list[str] = Form(default=[]),
):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_ADMIN_PERMISSOES)
    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    banco_dados = SessaoLocal()
    try:
        grupo = banco_dados.query(GrupoPermissao).filter(GrupoPermissao.id == id_grupo).first()
        if not grupo:
            return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, erro="Grupo nao encontrado.")

        lista_ids_permissoes = []
        for id_permissao in ids_permissoes:
            if id_permissao.isdigit():
                lista_ids_permissoes.append(int(id_permissao))

        permissoes_selecionadas = (
            banco_dados.query(Permissao).filter(Permissao.id.in_(lista_ids_permissoes)).all()
            if lista_ids_permissoes
            else []
        )
        grupo.descricao = descricao.strip()
        grupo.permissoes = permissoes_selecionadas
        banco_dados.commit()

        return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, mensagem="Permissoes do grupo atualizadas.")
    finally:
        banco_dados.close()


@roteador.post("/admin/permissoes/user-group")
async def associar_grupo_ao_usuario(
    request: Request,
    id_usuario: int = Form(...),
    id_grupo: int = Form(...),
):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_ADMIN_PERMISSOES)
    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    banco_dados = SessaoLocal()
    try:
        usuario = banco_dados.query(Usuario).filter(Usuario.id == id_usuario).first()
        grupo = banco_dados.query(GrupoPermissao).filter(GrupoPermissao.id == id_grupo).first()

        if not usuario or not grupo:
            return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, erro="Usuario ou grupo nao encontrado.")

        usuarios = banco_dados.query(Usuario).all()
        total_admin = contar_usuarios_admin(usuarios)
        if usuario_eh_admin(usuario) and grupo.nome != GRUPO_ADMIN and total_admin <= 1:
            return renderizar_admin_permissoes(
                request,
                banco_dados,
                usuario_autenticado.nome_usuario,
                erro="Nao e possivel remover o ultimo usuario administrador.",
            )

        usuario.grupos = [grupo]
        banco_dados.commit()

        return renderizar_admin_permissoes(request, banco_dados, usuario_autenticado.nome_usuario, mensagem="Grupo do usuario atualizado.")
    finally:
        banco_dados.close()


@roteador.get("/admin/usuario", response_class=HTMLResponse)
async def pagina_admin_usuarios(request: Request):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_ADMIN_PERMISSOES)
    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    banco_dados = SessaoLocal()
    try:
        garantir_dados_padrao_rbac(banco_dados)
        return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario)
    finally:
        banco_dados.close()


@roteador.post("/admin/usuario/create")
async def criar_usuario_admin(
    request: Request,
    nome_usuario: str = Form(...),
    senha: str = Form(...),
    id_grupo: str = Form(""),
):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_ADMIN_PERMISSOES)
    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    nome_usuario = nome_usuario.strip()
    senha = senha.strip()

    banco_dados = SessaoLocal()
    try:
        if len(nome_usuario) < 3:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Usuario deve ter ao menos 3 caracteres.")

        if len(senha) < 6:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Senha deve ter ao menos 6 caracteres.")

        usuario_existente = banco_dados.query(Usuario).filter(Usuario.nome_usuario == nome_usuario).first()
        if usuario_existente:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Este usuario ja existe.")

        grupo = carregar_grupo_por_id(banco_dados, id_grupo)
        if id_grupo and not grupo:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Grupo selecionado nao existe.")

        usuario_criado = criar_usuario(banco_dados, nome_usuario, senha)

        if grupo:
            usuario_criado.grupos = [grupo]
            banco_dados.commit()

        return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, mensagem="Usuario criado com sucesso.")
    finally:
        banco_dados.close()


@roteador.post("/admin/usuario/update/{id_usuario}")
async def atualizar_usuario_admin(
    request: Request,
    id_usuario: int,
    nome_usuario: str = Form(...),
    nova_senha: str = Form(""),
    id_grupo: str = Form(...),
):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_ADMIN_PERMISSOES)
    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    nome_usuario = nome_usuario.strip()
    nova_senha = nova_senha.strip()

    banco_dados = SessaoLocal()
    try:
        usuario = banco_dados.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Usuario nao encontrado.")

        if len(nome_usuario) < 3:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Usuario deve ter ao menos 3 caracteres.")

        usuario_duplicado = (
            banco_dados.query(Usuario)
            .filter(Usuario.nome_usuario == nome_usuario, Usuario.id != id_usuario)
            .first()
        )
        if usuario_duplicado:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Nome de usuario ja esta em uso.")

        grupo = carregar_grupo_por_id(banco_dados, id_grupo)
        if not grupo:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Grupo selecionado nao existe.")

        usuarios = banco_dados.query(Usuario).all()
        total_admin = contar_usuarios_admin(usuarios)
        if usuario_eh_admin(usuario) and grupo.nome != GRUPO_ADMIN and total_admin <= 1:
            return renderizar_admin_usuarios(
                request,
                banco_dados,
                usuario_autenticado.nome_usuario,
                erro="Nao e possivel remover o ultimo usuario administrador.",
            )

        if nova_senha and len(nova_senha) < 6:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Nova senha deve ter ao menos 6 caracteres.")

        usuario.nome_usuario = nome_usuario
        usuario.grupos = [grupo]

        if nova_senha:
            usuario.hash_senha = gerar_hash_senha(nova_senha)

        banco_dados.commit()

        usuario_sessao = request.session.get("auth_user")
        if usuario_sessao and usuario_sessao.get("id") == usuario.id:
            request.session["auth_user"]["nome_usuario"] = usuario.nome_usuario
            request.session.modified = True

        return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, mensagem="Usuario atualizado com sucesso.")
    finally:
        banco_dados.close()


@roteador.post("/admin/usuario/delete/{id_usuario}")
async def excluir_usuario_admin(request: Request, id_usuario: int):
    usuario_autenticado = exigir_permissao_web(request, PERMISSAO_ADMIN_PERMISSOES)
    if isinstance(usuario_autenticado, RedirectResponse):
        return usuario_autenticado

    banco_dados = SessaoLocal()
    try:
        usuario = banco_dados.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Usuario nao encontrado.")

        if usuario.id == usuario_autenticado.id:
            return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, erro="Voce nao pode excluir o proprio usuario.")

        usuarios = banco_dados.query(Usuario).all()
        total_admin = contar_usuarios_admin(usuarios)
        if usuario_eh_admin(usuario) and total_admin <= 1:
            return renderizar_admin_usuarios(
                request,
                banco_dados,
                usuario_autenticado.nome_usuario,
                erro="Nao e possivel excluir o ultimo usuario administrador.",
            )

        banco_dados.delete(usuario)
        banco_dados.commit()

        return renderizar_admin_usuarios(request, banco_dados, usuario_autenticado.nome_usuario, mensagem="Usuario excluido com sucesso.")
    finally:
        banco_dados.close()


def renderizar_admin_permissoes(request: Request, banco_dados, nome_usuario: str, mensagem: str = "", erro: str = ""):
    contexto = montar_contexto_admin_permissoes(banco_dados, mensagem=mensagem, erro=erro)
    contexto["nome_usuario"] = nome_usuario
    return modelos_html.TemplateResponse(
        name="admin_permissions.html",
        request=request,
        context=contexto,
        status_code=status.HTTP_200_OK,
    )


def renderizar_admin_usuarios(request: Request, banco_dados, nome_usuario: str, mensagem: str = "", erro: str = ""):
    contexto = montar_contexto_admin_usuarios(banco_dados, mensagem=mensagem, erro=erro)
    contexto["nome_usuario"] = nome_usuario
    return modelos_html.TemplateResponse(
        name="admin_users.html",
        request=request,
        context=contexto,
        status_code=status.HTTP_200_OK,
    )





