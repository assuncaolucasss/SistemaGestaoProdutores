"""
test_schemas_usuario.py — Testa validação de senha forte
=========================================================
A função validar_senha_forte está em routes/usuarios.py e também em schemas/usuario.py.
Testa via UsuarioCreate (o schema que a rota POST /usuarios/ usa).
"""

import pytest
from pydantic import ValidationError
from app.api.routes.usuarios import UsuarioCreate, validar_senha_forte


# ── Função utilitária validar_senha_forte ─────────────────────────────────────

class TestValidarSenhaForte:
    def test_senha_valida_retorna_a_propria_senha(self):
        assert validar_senha_forte("Senha@123") == "Senha@123"

    def test_rejeita_senha_curta(self):
        with pytest.raises(ValueError, match="mínimo 8 caracteres"):
            validar_senha_forte("Ab@1")

    def test_rejeita_sem_maiuscula(self):
        with pytest.raises(ValueError, match="letra maiúscula"):
            validar_senha_forte("senha@123")

    def test_rejeita_sem_minuscula(self):
        with pytest.raises(ValueError, match="letra minúscula"):
            validar_senha_forte("SENHA@123")

    def test_rejeita_sem_numero(self):
        with pytest.raises(ValueError, match="número"):
            validar_senha_forte("Senha@abc")

    def test_rejeita_sem_especial(self):
        with pytest.raises(ValueError, match="caractere especial"):
            validar_senha_forte("Senha1234")

    def test_mensagem_agrupa_multiplos_erros(self):
        with pytest.raises(ValueError) as exc_info:
            validar_senha_forte("abc")
        mensagem = str(exc_info.value)
        assert "mínimo 8 caracteres" in mensagem
        assert "letra maiúscula" in mensagem


# ── UsuarioCreate — integração com o field_validator ──────────────────────────

class TestUsuarioCreate:
    def test_cria_usuario_com_dados_validos(self):
        obj = UsuarioCreate(
            nome="Maria Silva",
            email="maria@email.com",
            senha="Senha@2026",
        )
        assert obj.nome == "Maria Silva"
        assert obj.email == "maria@email.com"
        assert obj.senha == "Senha@2026"

    def test_papel_padrao_e_usuario(self):
        from app.models.usuario import PapelUsuario
        obj = UsuarioCreate(
            nome="João",
            email="joao@email.com",
            senha="Forte@123",
        )
        assert obj.papel == PapelUsuario.usuario
        assert obj.ativo is True

    def test_rejeita_senha_fraca_via_schema(self):
        with pytest.raises(ValidationError) as exc_info:
            UsuarioCreate(
                nome="Teste",
                email="teste@email.com",
                senha="fraca",
            )
        erros = exc_info.value.errors()
        assert any("senha" in str(e["loc"]) for e in erros)

    def test_rejeita_email_invalido(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(
                nome="Teste",
                email="nao-e-um-email",
                senha="Forte@123",
            )
