from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

if TYPE_CHECKING:
    from app.models.produtor import Produtor
    from app.models.fomento import Fomento, ModalidadeClasse, ModalidadeSubclasse


class Submissao(SQLModel, table=True):
    __tablename__ = "submissoes_formulario"

    id:          Optional[int] = Field(default=None, primary_key=True)
    fomento_id:  int = Field(foreign_key="fomentos.id", index=True)
    produtor_id: int = Field(foreign_key="produtores.id", index=True)
    usuario_id:  int = Field(foreign_key="usuarios.id")

    classe_id:    Optional[int] = Field(default=None, foreign_key="modalidade_classes.id")
    subclasse_id: Optional[int] = Field(default=None, foreign_key="modalidade_subclasses.id")

    numero_processo: Optional[str] = Field(default=None, max_length=50)
    modalidade:      str           = Field(max_length=100)
    justificativa:   Optional[str] = None

    # ── Campos adicionados ──────────────────────────────────────────────────────
    entidade_elaboracao:        Optional[str] = Field(default=None, max_length=200)
    texto_entidade_responsavel: Optional[str] = None
    segundo_beneficiario_nome:  Optional[str] = Field(default=None, max_length=200)
    segundo_beneficiario_cpf:   Optional[str] = Field(default=None, max_length=20)
    # ───────────────────────────────────────────────────────────────────────────

    municipio_data:  Optional[str] = Field(default=None, max_length=100)
    data_assinatura: Optional[str] = Field(default=None, max_length=20)

    itens_investimento: Any = Field(default=None, sa_column=Column(JSONB))
    itens_mao_obra:     Any = Field(default=None, sa_column=Column(JSONB))

    criado_em:     datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

    produtor:  Optional["Produtor"]            = Relationship(back_populates="submissoes")
    fomento:   Optional["Fomento"]             = Relationship(back_populates="submissoes")
    classe:    Optional["ModalidadeClasse"]    = Relationship()
    subclasse: Optional["ModalidadeSubclasse"] = Relationship()