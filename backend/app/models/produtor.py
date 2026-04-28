from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime

if TYPE_CHECKING:
    from app.models.submissao import Submissao


class Produtor(SQLModel, table=True):
    __tablename__ = "produtores"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_beneficiario: Optional[str] = Field(default=None, max_length=50, index=True)

    # Colunas do XLSX
    cpf_beneficiario: str            = Field(max_length=14, unique=True, index=True)
    conjuge_nome:     Optional[str]  = Field(default=None, max_length=200)
    cpf_conjuge:      Optional[str]  = Field(default=None, max_length=14)
    situacao:         Optional[str]  = Field(default=None, max_length=200)
    data_homologacao: Optional[date] = None
    lote:             Optional[str]  = Field(default=None, max_length=100)

    # Identificação complementar
    nome_completo:   Optional[str]  = Field(default=None, max_length=200)
    data_nascimento: Optional[date] = None
    rg:              Optional[str]  = Field(default=None, max_length=20)
    orgao_emissor:   Optional[str]  = Field(default=None, max_length=30)
    telefone:        Optional[str]  = Field(default=None, max_length=20)
    email:           Optional[str]  = Field(default=None, max_length=150)

    # Localização
    municipio:    Optional[str] = Field(default=None, max_length=100)
    uf:           Optional[str] = Field(default="PA", max_length=2)
    endereco:     Optional[str] = Field(default=None, max_length=300)
    cep:          Optional[str] = Field(default=None, max_length=10)
    assentamento: Optional[str] = Field(default=None, max_length=200, index=True)
    comunidade:   Optional[str] = Field(default=None, max_length=200)  # ← adicionado

    # Atividade rural
    area_lote_ha:        Optional[float] = None
    atividade_principal: Optional[str]   = Field(default=None, max_length=200)
    dap_caf:             Optional[str]   = Field(default=None, max_length=50)
    data_dap_caf:        Optional[date]  = None

    # Controle
    ativo:         bool     = Field(default=True)
    criado_em:     datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

    # Relacionamentos
    submissoes: List["Submissao"] = Relationship(back_populates="produtor")
