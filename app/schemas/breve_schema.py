from pydantic import BaseModel

class BreveCreate(BaseModel):
    nome:str
    patente:str
    passaporte:str
    idade:str
    data_conclusao:str
    foto:str
    ano:str
    codigo:str