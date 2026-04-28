from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class CodigoRecuperacao(SQLModel, table=True):
    __tablename__ = "codigos_recuperacao"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    codigo: str
    expira_em: datetime
    usado: bool = Field(default=False)