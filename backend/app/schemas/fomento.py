from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


# ── Fomento ───────────────────────────────────────────────────────────────────
class FomentoCreate(BaseModel):
    nome:             str
    descricao:        Optional[str]  = None
    entidade_nome:    Optional[str]  = None
    entidade_edital:  Optional[str]  = None
    tecnico_nome:     Optional[str]  = None
    tecnico_cfta:     Optional[str]  = None
    tecnico_telefone: Optional[str]  = None
    modalidades:      Optional[list] = None
    ativo:            bool           = True

class FomentoUpdate(BaseModel):
    nome:             Optional[str]  = None
    descricao:        Optional[str]  = None
    entidade_nome:    Optional[str]  = None
    entidade_edital:  Optional[str]  = None
    tecnico_nome:     Optional[str]  = None
    tecnico_cfta:     Optional[str]  = None
    tecnico_telefone: Optional[str]  = None
    modalidades:      Optional[list] = None
    ativo:            Optional[bool] = None

class FomentoRead(BaseModel):
    id:               int
    nome:             str
    descricao:        Optional[str]
    entidade_nome:    Optional[str]
    entidade_edital:  Optional[str]
    tecnico_nome:     Optional[str]
    tecnico_cfta:     Optional[str]
    tecnico_telefone: Optional[str]
    modalidades:      Optional[list]
    ativo:            bool
    criado_em:        datetime

    model_config = {"from_attributes": True}


# ── ModalidadeClasse ──────────────────────────────────────────────────────────
class ModalidadeClasseCreate(BaseModel):
    fomento_id: int
    nome:       str
    escopo:     str  # "8k" ou "16k"

class ModalidadeClasseUpdate(BaseModel):
    nome:  Optional[str]  = None
    ativo: Optional[bool] = None

class ModalidadeClasseRead(BaseModel):
    id:         int
    fomento_id: int
    nome:       str
    escopo:     str
    ativo:      bool
    criado_em:  datetime

    model_config = {"from_attributes": True}


# ── ModalidadeSubclasse ───────────────────────────────────────────────────────
class ModalidadeSubclasseCreate(BaseModel):
    fomento_id: int
    nome:       str
    escopo:     str  # "8k" ou "16k"
    classe_id:  Optional[int] = None  # obrigatório para escopo "16k"

class ModalidadeSubclasseUpdate(BaseModel):
    nome:  Optional[str]  = None
    ativo: Optional[bool] = None

class ModalidadeSubclasseRead(BaseModel):
    id:         int
    fomento_id: int
    nome:       str
    escopo:     str
    ativo:      bool
    criado_em:  datetime

    model_config = {"from_attributes": True}


# ── Itens de características ──────────────────────────────────────────────────
class ItemMemoria(BaseModel):
    discriminacao:  str   = ''
    quantidade:     float = 0
    valor_unitario: float = 0
    subtotal:       float = 0

class ItemMaoObra(BaseModel):
    descricao:      str   = ''
    visitas:        float = 0  # equivale a "qtd" no frontend
    valor_unitario: float = 0
    subtotal:       float = 0


# ── CaracteristicaModalidade ──────────────────────────────────────────────────
class CaracteristicaCreate(BaseModel):
    classe_id:                  int
    subclasse_id:               int
    justificativa:              Optional[str]            = None
    entidade_elaboracao:        Optional[str]            = None  # ← adicionado
    texto_entidade_responsavel: Optional[str]            = None  # ← adicionado
    memoria_calculo:            List[ItemMemoria]        = []    # ← tipado
    mao_obra_especializada:     List[ItemMaoObra]        = []    # ← tipado

class CaracteristicaUpdate(BaseModel):
    justificativa:              Optional[str]            = None
    entidade_elaboracao:        Optional[str]            = None  # ← adicionado
    texto_entidade_responsavel: Optional[str]            = None  # ← adicionado
    memoria_calculo:            Optional[List[ItemMemoria]] = None  # ← tipado
    mao_obra_especializada:     Optional[List[ItemMaoObra]] = None  # ← tipado

class CaracteristicaRead(BaseModel):
    id:                         int
    classe_id:                  int
    subclasse_id:               int
    justificativa:              Optional[str]  = None
    entidade_elaboracao:        Optional[str]  = None  # ← adicionado
    texto_entidade_responsavel: Optional[str]  = None  # ← adicionado
    memoria_calculo:            List[Any]      = []
    mao_obra_especializada:     List[Any]      = []
    criado_em:                  datetime
    atualizado_em:              datetime

    model_config = {"from_attributes": True}


# ── Resposta hierárquica ──────────────────────────────────────────────────────
class SubclasseComCaracteristica(BaseModel):
    subclasse:      ModalidadeSubclasseRead
    caracteristica: Optional[CaracteristicaRead] = None

class ClasseComSubclasses(BaseModel):
    classe:     ModalidadeClasseRead
    subclasses: List[SubclasseComCaracteristica]

class HierarquiaFomentoRead(BaseModel):
    fomento:    FomentoRead
    hierarquia: List[ClasseComSubclasses]