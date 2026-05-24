import base64
import hashlib
import hmac
import os

from app.database.models import Usuario
from app.services.rbac_service import atribuir_grupo_padrao_para_usuario


def gerar_hash_senha_com_sal(senha: str, sal: bytes) -> str:
    senha_bytes = senha.encode("utf-8")
    resumo = hashlib.pbkdf2_hmac("sha256", senha_bytes, sal, 120_000)
    return base64.b64encode(resumo).decode("utf-8")


def gerar_hash_senha(senha: str) -> str:
    sal = os.urandom(16)
    sal_b64 = base64.b64encode(sal).decode("utf-8")
    hash_b64 = gerar_hash_senha_com_sal(senha, sal)
    return f"{sal_b64}:{hash_b64}"


def validar_senha(senha: str, hash_senha: str) -> bool:
    partes = hash_senha.split(":")

    if len(partes) != 2:
        return False

    sal_b64, hash_esperado = partes

    try:
        sal = base64.b64decode(sal_b64.encode("utf-8"))
    except Exception:
        return False

    hash_atual = gerar_hash_senha_com_sal(senha, sal)
    return hmac.compare_digest(hash_atual, hash_esperado)


def buscar_usuario_por_nome_usuario(banco_dados, nome_usuario: str):
    return banco_dados.query(Usuario).filter(Usuario.nome_usuario == nome_usuario).first()


def criar_usuario(banco_dados, nome_usuario: str, senha: str):
    usuario = Usuario(
        nome_usuario=nome_usuario.strip(),
        hash_senha=gerar_hash_senha(senha)
    )
    banco_dados.add(usuario)
    banco_dados.commit()
    banco_dados.refresh(usuario)
    atribuir_grupo_padrao_para_usuario(banco_dados, usuario)
    banco_dados.refresh(usuario)
    return usuario


