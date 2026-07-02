from pydantic import BaseModel
from typing import Optional, List, Any
from app.schemas.produtor import ProdutorRead
from app.schemas.fomento import FomentoRead, ModalidadeClasseRead, ModalidadeSubclasseRead


class ItemInvestimentoRead(BaseModel):
    discriminacao:  str
    quantidade:     float
    valor_unitario: float
    subtotal:       float


class ItemMaoObraRead(BaseModel):
    descricao:      str
    visitas:        float   # float para aceitar decimais vindos do JS
    valor_unitario: float
    subtotal:       float


class CaracteristicaFormulario(BaseModel):
    id:                         int
    justificativa:              Optional[str] = None
    entidade_elaboracao:        Optional[str] = None
    texto_entidade_responsavel: Optional[str] = None
    # ← nomes que o watcher do Vue espera
    itens_investimento:         List[ItemInvestimentoRead] = []
    itens_mao_obra:             List[ItemMaoObraRead]      = []


class FormularioDadosRead(BaseModel):
    produtor:        ProdutorRead
    fomento:         FomentoRead
    classe:          Optional[ModalidadeClasseRead]     = None
    subclasse:       Optional[ModalidadeSubclasseRead]  = None
    caracteristica:  Optional[CaracteristicaFormulario] = None
    submissao_id:    Optional[int]  = None
    numero_processo: Optional[str]  = None
    municipio_data:  Optional[str]  = None
    data_assinatura: Optional[str]  = None

    model_config = {"from_attributes": True}
