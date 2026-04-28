"""
test_schemas_produtor.py — Testa os validators de ProdutorUpdate/ProdutorRead
=============================================================================
Cobre normalizar_cpf e vazio_para_none, que são regras de domínio críticas
porque o CPF chega sem máscara do XLSX e precisa ser formatado antes de salvar.
"""

import pytest
from pydantic import ValidationError
from app.schemas.produtor import ProdutorUpdate, normalizar_cpf


# ── normalizar_cpf (função utilitária) ────────────────────────────────────────

class TestNormalizarCpf:
    def test_cpf_sem_mascara_vira_formatado(self):
        assert normalizar_cpf("12345678901") == "123.456.789-01"

    def test_cpf_ja_formatado_permanece(self):
        assert normalizar_cpf("123.456.789-01") == "123.456.789-01"

    def test_cpf_com_espacos_e_caracteres(self):
        # Remove tudo que não é dígito antes de formatar
        assert normalizar_cpf("123 456 789-01") == "123.456.789-01"

    def test_cpf_none_retorna_none(self):
        assert normalizar_cpf(None) is None

    def test_cpf_vazio_retorna_vazio(self):
        # String vazia não tem 11 dígitos, retorna como veio
        assert normalizar_cpf("") == ""

    def test_cpf_com_menos_de_11_digitos_retorna_original(self):
        resultado = normalizar_cpf("12345")
        assert resultado == "12345"


# ── ProdutorUpdate — field_validator cpf_beneficiario ─────────────────────────

class TestProdutorUpdateCpf:
    def test_cpf_normalizado_no_schema(self):
        obj = ProdutorUpdate(cpf_beneficiario="98765432100")
        assert obj.cpf_beneficiario == "987.654.321-00"

    def test_cpf_conjuge_normalizado(self):
        obj = ProdutorUpdate(cpf_conjuge="11122233344")
        assert obj.cpf_conjuge == "111.222.333-44"

    def test_cpf_none_aceito(self):
        obj = ProdutorUpdate(cpf_beneficiario=None)
        assert obj.cpf_beneficiario is None


# ── ProdutorUpdate — vazio_para_none em campos de data e área ─────────────────

class TestProdutorUpdateVazioParaNone:
    def test_data_nascimento_vazia_vira_none(self):
        obj = ProdutorUpdate(data_nascimento="")
        assert obj.data_nascimento is None

    def test_data_homologacao_vazia_vira_none(self):
        obj = ProdutorUpdate(data_homologacao="")
        assert obj.data_homologacao is None

    def test_data_dap_caf_vazia_vira_none(self):
        obj = ProdutorUpdate(data_dap_caf="")
        assert obj.data_dap_caf is None

    def test_area_lote_ha_zero_vira_none(self):
        obj = ProdutorUpdate(area_lote_ha=0)
        assert obj.area_lote_ha is None

    def test_area_lote_ha_valida_permanece(self):
        obj = ProdutorUpdate(area_lote_ha=3.5)
        assert obj.area_lote_ha == 3.5

    def test_data_valida_permanece(self):
        from datetime import date
        obj = ProdutorUpdate(data_nascimento=date(1990, 5, 15))
        assert obj.data_nascimento == date(1990, 5, 15)
