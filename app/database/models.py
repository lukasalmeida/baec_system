from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


tabela_usuario_grupos = Table(
    "user_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("permission_groups.id"), primary_key=True),
)


tabela_grupo_permissoes = Table(
    "group_permissions",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("permission_groups.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class Breve(Base):
    __tablename__ = "breves"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    patente = Column(String)
    passaporte = Column(String)
    idade = Column(String)
    data_conclusao = Column(String)
    foto = Column(String)
    ano = Column(Integer)
    codigo = Column(String)
    numero_sequencial = Column(Integer)
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())


class Usuario(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nome_usuario = Column("username", String, unique=True, nullable=False, index=True)
    hash_senha = Column("password_hash", String, nullable=False)
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    grupos = relationship(
        "GrupoPermissao",
        secondary=tabela_usuario_grupos,
        back_populates="usuarios",
    )


class Permissao(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column("code", String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False)
    descricao = Column("description", String, nullable=True)
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    grupos = relationship(
        "GrupoPermissao",
        secondary=tabela_grupo_permissoes,
        back_populates="permissoes",
    )


class GrupoPermissao(Base):
    __tablename__ = "permission_groups"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column("name", String, unique=True, nullable=False, index=True)
    descricao = Column("description", String, nullable=True)
    criado_em = Column("created_at", DateTime(timezone=True), server_default=func.now())
    usuarios = relationship(
        "Usuario",
        secondary=tabela_usuario_grupos,
        back_populates="grupos",
    )
    permissoes = relationship(
        "Permissao",
        secondary=tabela_grupo_permissoes,
        back_populates="grupos",
    )


