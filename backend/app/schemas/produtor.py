import re
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime


def normalizar_cpf(cpf: Optional[str]) -> Optional[str]:
    if not cpf:
        return cpf
    apenas_digitos = re.sub(r'\D', '', cpf)   # ← era r'\\D' (double escape errado)
    if len(apenas_digitos) == 11:
        return f"{apenas_digitos[:3]}.{apenas_digitos[3:6]}.{apenas_digitos[6:9]}-{apenas_digitos[9:]}"
    return cpf


def vazio_para_none(v):
    if v == '' or v == 0:
        return None
    return v


class ProdutorRead(BaseModel):
    id:                  int
    cpf_beneficiario:    str
    codigo_beneficiario: Optional[str]   = None
    conjuge_nome:        Optional[str]   = None
    cpf_conjuge:         Optional[str]   = None
    situacao:            Optional[str]   = None
    data_homologacao:    Optional[date]  = None
    lote:                Optional[str]   = None
    nome_completo:       Optional[str]   = None
    data_nascimento:     Optional[date]  = None
    rg:                  Optional[str]   = None
    orgao_emissor:       Optional[str]   = None
    telefone:            Optional[str]   = None
    email:               Optional[str]   = None
    municipio:           Optional[str]   = None
    uf:                  Optional[str]   = None
    endereco:            Optional[str]   = None
    cep:                 Optional[str]   = None
    comunidade:          Optional[str]   = None
    area_lote_ha:        Optional[float] = None
    atividade_principal: Optional[str]   = None
    dap_caf:             Optional[str]   = None
    data_dap_caf:        Optional[date]  = None
    assentamento:        Optional[str]   = None
    ativo:               bool
    criado_em:           datetime
    atualizado_em:       datetime

    @field_validator('cpf_beneficiario', mode='before')
    @classmethod
    def formatar_cpf(cls, v):
        return normalizar_cpf(v)

    @field_validator('cpf_conjuge', mode='before')
    @classmethod
    def formatar_cpf_conjuge(cls, v):
        return normalizar_cpf(v)

    class Config:
        from_attributes = True


class ProdutorUpdate(BaseModel):
    cpf_beneficiario:    Optional[str]   = None
    codigo_beneficiario: Optional[str]   = None
    conjuge_nome:        Optional[str]   = None
    cpf_conjuge:         Optional[str]   = None
    situacao:            Optional[str]   = None
    data_homologacao:    Optional[date]  = None
    lote:                Optional[str]   = None
    nome_completo:       Optional[str]   = None
    data_nascimento:     Optional[date]  = None
    rg:                  Optional[str]   = None
    orgao_emissor:       Optional[str]   = None
    telefone:            Optional[str]   = None
    email:               Optional[str]   = None
    municipio:           Optional[str]   = None
    uf:                  Optional[str]   = None
    endereco:            Optional[str]   = None
    cep:                 Optional[str]   = None
    comunidade:          Optional[str]   = None
    area_lote_ha:        Optional[float] = None
    atividade_principal: Optional[str]   = None
    dap_caf:             Optional[str]   = None
    data_dap_caf:        Optional[date]  = None
    assentamento:        Optional[str]   = None
    ativo:               Optional[bool]  = None

    @field_validator('cpf_beneficiario', mode='before')
    @classmethod
    def formatar_cpf(cls, v):
        return normalizar_cpf(v)

    @field_validator('cpf_conjuge', mode='before')
    @classmethod
    def formatar_cpf_conjuge(cls, v):
        return normalizar_cpf(v)

    @field_validator('data_nascimento', 'data_homologacao', 'data_dap_caf', mode='before')
    @classmethod
    def tratar_datas(cls, v):
        return vazio_para_none(v)

    @field_validator('area_lote_ha', mode='before')
    @classmethod
    def tratar_area(cls, v):
        return vazio_para_none(v)