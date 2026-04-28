from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class PapelUsuario(str, Enum):
    usuario = "usuario"
    superusuario = "superusuario"

class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id:          Optional[int] = Field(default=None, primary_key=True)
    nome:        str = Field(max_length=150)
    email:       str = Field(max_length=150, unique=True, index=True)
    senha_hash:  str
    papel:       PapelUsuario = Field(default=PapelUsuario.usuario)
    ativo:       bool = Field(default=True)
    criado_em:   datetime = Field(default_factory=datetime.now)
