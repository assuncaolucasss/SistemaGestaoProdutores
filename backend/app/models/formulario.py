from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from app.models.fomento import Fomento

class TipoCampo(str):
    texto   = "texto"
    numero  = "numero"
    data    = "data"
    select  = "select"
    boolean = "boolean"

class ModeloCampoFormulario(SQLModel, table=True):
    __tablename__ = "modelo_campos_formulario"

    id:          Optional[int] = Field(default=None, primary_key=True)
    fomento_id:  int = Field(foreign_key="fomentos.id", index=True)
    nome_campo:  str = Field(max_length=100)
    rotulo:      str = Field(max_length=200)
    tipo:        str = Field(default="texto", max_length=30)
    opcoes:      Optional[Any] = Field(
                     default=None,
                     sa_column=Column(JSONB)
                 )
    obrigatorio: bool = Field(default=False)
    ordem:       int  = Field(default=0)
