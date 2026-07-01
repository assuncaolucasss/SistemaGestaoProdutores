from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.produtor import ProdutorRead
from app.schemas.fomento import (
    FomentoRead,
    ModalidadeClasseRead,
    ModalidadeSubclasseRead,
)


class ItemInvestimentoRead(BaseModel):
    discriminacao: str
    quantidade: float
    valor_unitario: float
    subtotal: float


class ItemMaoObraRead(BaseModel):
    descricao: str
    visitas: float
    valor_unitario: float
    subtotal: float


class CaracteristicaFormulario(BaseModel):
    id: int
    justificativa: Optional[str] = None
    entidade_elaboracao: Optional[str] = None
    texto_entidade_responsavel: Optional[str] = None
    itens_investimento: List[ItemInvestimentoRead] = Field(default_factory=list)
    itens_mao_obra: List[ItemMaoObraRead] = Field(default_factory=list)


class FormularioDadosRead(BaseModel):
    produtor: ProdutorRead
    fomento: FomentoRead
    classe: Optional[ModalidadeClasseRead] = None
    subclasse: Optional[ModalidadeSubclasseRead] = None
    caracteristica: Optional[CaracteristicaFormulario] = None
    submissao_id: Optional[int] = None
    numero_processo: Optional[str] = None
    municipio_data: Optional[str] = None
    data_assinatura: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
