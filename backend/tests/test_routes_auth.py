"""
test_routes_auth.py — Testa /auth/token, /auth/me e recuperação de senha
"""
import pytest
from datetime import datetime, timedelta
from app.models.usuario import Usuario, PapelUsuario
from app.models.codigo_recuperacao import CodigoRecuperacao
from app.core.security import hash_senha


def seed_usuario_ativo(session):
    u = Usuario(
        id=50,
        nome="Lucas Auth",
        email="lucas@auth.com",
        senha_hash=hash_senha("Senha@2026"),
        papel=PapelUsuario.usuario,
        ativo=True,
    )
    session.add(u)
    session.commit()


def seed_usuario_inativo(session):
    u = Usuario(
        id=51,
        nome="Inativo",
        email="inativo@auth.com",
        senha_hash=hash_senha("Senha@2026"),
        papel=PapelUsuario.usuario,
        ativo=False,
    )
    session.add(u)
    session.commit()


class TestLogin:
    def test_login_valido_retorna_token(self, client, session):
        seed_usuario_ativo(session)
        resp = client.post("/auth/token", data={
            "username": "lucas@auth.com",
            "password": "Senha@2026",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_senha_errada_retorna_401(self, client, session):
        seed_usuario_ativo(session)
        resp = client.post("/auth/token", data={
            "username": "lucas@auth.com",
            "password": "SenhaErrada@1",
        })
        assert resp.status_code == 401

    def test_login_email_inexistente_retorna_401(self, client):
        resp = client.post("/auth/token", data={
            "username": "naoexiste@email.com",
            "password": "Senha@2026",
        })
        assert resp.status_code == 401

    def test_login_usuario_inativo_retorna_400(self, client, session):
        seed_usuario_inativo(session)
        resp = client.post("/auth/token", data={
            "username": "inativo@auth.com",
            "password": "Senha@2026",
        })
        assert resp.status_code == 400


class TestRecuperacaoSenha:
    def test_email_inexistente_retorna_mensagem_generica(self, client):
        # Não deve revelar se o e-mail existe ou não (segurança)
        resp = client.post("/auth/recuperar-senha", json={"email": "naoexiste@email.com"})
        assert resp.status_code == 200
        assert "receberá o código" in resp.json()["mensagem"]

    def test_verificar_codigo_invalido_retorna_400(self, client):
        resp = client.post("/auth/verificar-codigo", json={
            "email": "lucas@auth.com",
            "codigo": "000000",
        })
        assert resp.status_code == 400

    def test_verificar_codigo_expirado_retorna_400(self, client, session):
        seed_usuario_ativo(session)
        codigo_expirado = CodigoRecuperacao(
            email="lucas@auth.com",
            codigo="123456",
            expira_em=datetime.now() - timedelta(minutes=10),
            usado=False,
        )
        session.add(codigo_expirado)
        session.commit()

        resp = client.post("/auth/verificar-codigo", json={
            "email": "lucas@auth.com",
            "codigo": "123456",
        })
        assert resp.status_code == 400
        assert "expirado" in resp.json()["detail"]

    def test_verificar_codigo_valido_retorna_200(self, client, session):
        seed_usuario_ativo(session)
        codigo_valido = CodigoRecuperacao(
            email="lucas@auth.com",
            codigo="654321",
            expira_em=datetime.now() + timedelta(minutes=5),
            usado=False,
        )
        session.add(codigo_valido)
        session.commit()

        resp = client.post("/auth/verificar-codigo", json={
            "email": "lucas@auth.com",
            "codigo": "654321",
        })
        assert resp.status_code == 200

    def test_nova_senha_com_codigo_valido(self, client, session):
        seed_usuario_ativo(session)
        codigo = CodigoRecuperacao(
            email="lucas@auth.com",
            codigo="999888",
            expira_em=datetime.now() + timedelta(minutes=5),
            usado=False,
        )
        session.add(codigo)
        session.commit()

        resp = client.post("/auth/nova-senha", json={
            "email": "lucas@auth.com",
            "codigo": "999888",
            "nova_senha": "NovaSenha@2026",
        })
        assert resp.status_code == 200
        assert "sucesso" in resp.json()["mensagem"]
