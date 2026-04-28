from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Any, TYPE_CHECKING
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

if TYPE_CHECKING:
    from app.models.submissao import Submissao


class Fomento(SQLModel, table=True):
    __tablename__ = "fomentos"

    id:        Optional[int] = Field(default=None, primary_key=True)
    nome:      str = Field(max_length=200, unique=True, index=True)
    descricao: Optional[str] = None

    entidade_nome:    Optional[str] = Field(default=None, max_length=300)
    entidade_edital:  Optional[str] = Field(default=None, max_length=200)
    tecnico_nome:     Optional[str] = Field(default=None, max_length=200)
    tecnico_cfta:     Optional[str] = Field(default=None, max_length=50)
    tecnico_telefone: Optional[str] = Field(default=None, max_length=20)

    modalidades: Any = Field(default=None, sa_column=Column(JSONB))

    ativo:     bool     = Field(default=True)
    criado_em: datetime = Field(default_factory=datetime.now)

    submissoes: List["Submissao"] = Relationship(back_populates="fomento")
    classes:    List["ModalidadeClasse"] = Relationship(back_populates="fomento")


class ModalidadeClasse(SQLModel, table=True):
    __tablename__ = "modalidade_classes"

    id:         Optional[int] = Field(default=None, primary_key=True)
    fomento_id: int           = Field(foreign_key="fomentos.id", index=True)
    nome:       str           = Field(max_length=200)
    escopo:     str           = Field(max_length=3)
    ativo:      bool          = Field(default=True)
    criado_em:  datetime      = Field(default_factory=datetime.now)

    fomento:         Optional["Fomento"]               = Relationship(back_populates="classes")
    caracteristicas: List["CaracteristicaModalidade"]  = Relationship(back_populates="classe")


class ModalidadeSubclasse(SQLModel, table=True):
    __tablename__ = "modalidade_subclasses"

    id:         Optional[int] = Field(default=None, primary_key=True)
    fomento_id: int           = Field(foreign_key="fomentos.id", index=True)
    nome:       str           = Field(max_length=200)
    escopo:     str           = Field(max_length=3)
    ativo:      bool          = Field(default=True)
    criado_em:  datetime      = Field(default_factory=datetime.now)

    caracteristicas: List["CaracteristicaModalidade"] = Relationship(back_populates="subclasse")


class CaracteristicaModalidade(SQLModel, table=True):
    __tablename__ = "caracteristicas_modalidade"

    id:           Optional[int] = Field(default=None, primary_key=True)
    classe_id:    int           = Field(foreign_key="modalidade_classes.id", index=True)
    subclasse_id: int           = Field(foreign_key="modalidade_subclasses.id", index=True)

    justificativa:              Optional[str] = None
    # ── Campos adicionados ──────────────────────────────────────────────────────
    entidade_elaboracao:        Optional[str] = Field(default=None, max_length=200)
    texto_entidade_responsavel: Optional[str] = None
    # ───────────────────────────────────────────────────────────────────────────
    memoria_calculo:        Any = Field(default=None, sa_column=Column(JSONB))
    mao_obra_especializada: Any = Field(default=None, sa_column=Column(JSONB))

    criado_em:     datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

    classe:    Optional["ModalidadeClasse"]    = Relationship(back_populates="caracteristicas")
    subclasse: Optional["ModalidadeSubclasse"] = Relationship(back_populates="caracteristicas")