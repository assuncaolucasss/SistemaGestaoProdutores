# app/models/recuperacao_senha.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class RecuperacaoSenha(SQLModel, table=True):
    __tablename__ = "recuperacao_senha"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    codigo: str
    usado: bool = Field(default=False)
    criado_em: datetime = Field(default_factory=datetime.now)
    expira_em: datetime
