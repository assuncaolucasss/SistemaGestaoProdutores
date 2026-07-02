schemas/submissão.py

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ItemInvestimento(BaseModel):
    discriminacao: str
    quantidade: float
    valor_unitario: float
    subtotal: float


class ItemMaoObra(BaseModel):
    descricao: str
    visitas: float
    valor_unitario: float
    subtotal: float


class SubmissaoCreate(BaseModel):
    fomento_id: int
    produtor_id: int
    numero_processo: Optional[str] = None
    modalidade: str
    classe_id: Optional[int] = None
    subclasse_id: Optional[int] = None
    justificativa: Optional[str] = None
    entidade_elaboracao: Optional[str] = None
    texto_entidade_responsavel: Optional[str] = None
    segundo_beneficiario_nome: Optional[str] = None
    segundo_beneficiario_cpf: Optional[str] = None
    municipio_data: Optional[str] = None
    data_assinatura: Optional[str] = None
    itens_investimento: List[ItemInvestimento] = Field(default_factory=list)
    itens_mao_obra: List[ItemMaoObra] = Field(default_factory=list)


class SubmissaoUpdate(BaseModel):
    modalidade: Optional[str] = None
    numero_processo: Optional[str] = None
    classe_id: Optional[int] = None
    subclasse_id: Optional[int] = None
    justificativa: Optional[str] = None
    entidade_elaboracao: Optional[str] = None
    texto_entidade_responsavel: Optional[str] = None
    segundo_beneficiario_nome: Optional[str] = None
    segundo_beneficiario_cpf: Optional[str] = None
    municipio_data: Optional[str] = None
    data_assinatura: Optional[str] = None
    itens_investimento: List[ItemInvestimento] = Field(default_factory=list)
    itens_mao_obra: List[ItemMaoObra] = Field(default_factory=list)


class SubmissaoRead(BaseModel):
    id: int
    fomento_id: int
    produtor_id: int
    usuario_id: int
    classe_id: Optional[int] = None
    subclasse_id: Optional[int] = None
    numero_processo: Optional[str] = None
    modalidade: str
    justificativa: Optional[str] = None
    entidade_elaboracao: Optional[str] = None
    texto_entidade_responsavel: Optional[str] = None
    segundo_beneficiario_nome: Optional[str] = None
    segundo_beneficiario_cpf: Optional[str] = None
    municipio_data: Optional[str] = None
    data_assinatura: Optional[str] = None
    itens_investimento: List[ItemInvestimento] = Field(default_factory=list)
    itens_mao_obra: List[ItemMaoObra] = Field(default_factory=list)
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)
