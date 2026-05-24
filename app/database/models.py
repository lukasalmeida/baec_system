from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from app.database.base import Base


class Breve(Base):
    __tablename__ = "breves"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    patente = Column(String)
    passaporte = Column(String)
    idade = Column(String)
    data_conclusao = Column(String)
    foto = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
