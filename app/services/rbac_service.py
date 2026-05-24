from app.database.models import GrupoPermissao
from app.database.models import Permissao
from app.database.models import Usuario


PERMISSAO_GERAR_BREVE = "gerar_breve"
PERMISSAO_ADMIN_PERMISSOES = "admin_permissoes"

GRUPO_ADMIN = "Admin"
GRUPO_OPERADOR = "Operador"


def obter_ou_criar_permissao(banco_dados, codigo: str, nome: str, descricao: str):
    permissao = banco_dados.query(Permissao).filter(Permissao.codigo == codigo).first()

    if permissao:
        if permissao.nome != nome or permissao.descricao != descricao:
            permissao.nome = nome
            permissao.descricao = descricao
            banco_dados.flush()
        return permissao

    permissao = Permissao(codigo=codigo, nome=nome, descricao=descricao)
    banco_dados.add(permissao)
    banco_dados.flush()
    return permissao


def obter_ou_criar_grupo(banco_dados, nome: str, descricao: str):
    grupo = banco_dados.query(GrupoPermissao).filter(GrupoPermissao.nome == nome).first()

    if grupo:
        if grupo.descricao != descricao:
            grupo.descricao = descricao
            banco_dados.flush()
        return grupo

    grupo = GrupoPermissao(nome=nome, descricao=descricao)
    banco_dados.add(grupo)
    banco_dados.flush()
    return grupo


def garantir_permissao_no_grupo(grupo: GrupoPermissao, permissao: Permissao):
    if permissao not in grupo.permissoes:
        grupo.permissoes.append(permissao)


def garantir_dados_padrao_rbac(banco_dados):
    permissao_gerar_breve = obter_ou_criar_permissao(
        banco_dados,
        codigo=PERMISSAO_GERAR_BREVE,
        nome="Gerar breve",
        descricao="Permite gerar e salvar novos breves.",
    )
    permissao_admin = obter_ou_criar_permissao(
        banco_dados,
        codigo=PERMISSAO_ADMIN_PERMISSOES,
        nome="Administrar permissoes",
        descricao="Permite gerenciar grupos, permissoes e vinculos de usuarios.",
    )

    grupo_admin = obter_ou_criar_grupo(
        banco_dados,
        nome=GRUPO_ADMIN,
        descricao="Grupo administrativo com acesso total.",
    )
    grupo_operador = obter_ou_criar_grupo(
        banco_dados,
        nome=GRUPO_OPERADOR,
        descricao="Grupo operacional para geracao de breve.",
    )

    garantir_permissao_no_grupo(grupo_admin, permissao_gerar_breve)
    garantir_permissao_no_grupo(grupo_admin, permissao_admin)

    if not grupo_operador.permissoes:
        garantir_permissao_no_grupo(grupo_operador, permissao_gerar_breve)

    usuarios = banco_dados.query(Usuario).order_by(Usuario.id.asc()).all()
    existe_usuario_admin = any(
        any(grupo.nome == GRUPO_ADMIN for grupo in usuario.grupos)
        for usuario in usuarios
    )

    for usuario in usuarios:
        if usuario.grupos:
            continue

        if not existe_usuario_admin:
            usuario.grupos = [grupo_admin]
            existe_usuario_admin = True
        else:
            usuario.grupos = [grupo_operador]

    banco_dados.commit()


def obter_permissoes_usuario(banco_dados, id_usuario: int):
    usuario = banco_dados.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        return set()

    permissoes = set()
    for grupo in usuario.grupos:
        for permissao in grupo.permissoes:
            permissoes.add(permissao.codigo)

    return permissoes


def usuario_tem_permissao(banco_dados, id_usuario: int, codigo_permissao: str) -> bool:
    permissoes = obter_permissoes_usuario(banco_dados, id_usuario)
    return codigo_permissao in permissoes


def atribuir_grupo_padrao_para_usuario(banco_dados, usuario: Usuario):
    if usuario.grupos:
        return

    garantir_dados_padrao_rbac(banco_dados)

    quantidade_usuarios = banco_dados.query(Usuario).count()
    nome_grupo_alvo = GRUPO_ADMIN if quantidade_usuarios == 1 else GRUPO_OPERADOR
    grupo = banco_dados.query(GrupoPermissao).filter(GrupoPermissao.nome == nome_grupo_alvo).first()

    if not grupo:
        return

    usuario.grupos = [grupo]
    banco_dados.commit()


