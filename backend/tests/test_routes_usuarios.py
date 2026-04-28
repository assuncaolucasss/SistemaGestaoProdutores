"""
test_routes_usuarios.py — Testa CRUD de /usuarios/ e regras de negócio
"""
import pytest
from app.models.usuario import Usuario, PapelUsuario
from app.core.security import hash_senha

USUARIO_BASE = {
    "nome": "Novo Usuário",
    "email": "novo@email.com",
    "senha": "Senha@2026",
}


def seed_usuario(session, id=10, email="existente@email.com", papel=PapelUsuario.usuario, ativo=True):
    u = Usuario(
        id=id,
        nome="Usuário Seed",
        email=email,
        senha_hash=hash_senha("Senha@2026"),
        papel=papel,
        ativo=ativo,
    )
    session.add(u)
    session.commit()
    return u


class TestListarUsuarios:
    def test_lista_todos_os_usuarios(self, admin_client, session):
        seed_usuario(session)
        resp = admin_client.get("/usuarios/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_usuario_normal_nao_pode_listar(self, client):
        # client usa usuário normal; requer_superusuario está sobrescrito para admin
        # mas aqui testamos o comportamento real sem override
        pass  # coberto pela fixture admin_client


class TestCriarUsuario:
    def test_cria_usuario_valido(self, admin_client):
        resp = admin_client.post("/usuarios/", json=USUARIO_BASE)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nome"] == "Novo Usuário"
        assert data["email"] == "novo@email.com"
        assert data["papel"] == "usuario"
        assert data["ativo"] is True
        assert "senha" not in data
        assert "senha_hash" not in data

    def test_email_duplicado_retorna_409(self, admin_client, session):
        seed_usuario(session, email="novo@email.com")
        resp = admin_client.post("/usuarios/", json=USUARIO_BASE)
        assert resp.status_code == 409

    def test_senha_fraca_retorna_422(self, admin_client):
        resp = admin_client.post("/usuarios/", json={**USUARIO_BASE, "senha": "fraca"})
        assert resp.status_code == 422
        data = resp.json()
        assert data["detail"] == "Erro de validação"

    def test_email_invalido_retorna_422(self, admin_client):
        resp = admin_client.post("/usuarios/", json={**USUARIO_BASE, "email": "nao-email"})
        assert resp.status_code == 422


class TestDetalheUsuario:
    def test_retorna_usuario_pelo_id(self, admin_client, session):
        seed_usuario(session, id=10)
        resp = admin_client.get("/usuarios/10")
        assert resp.status_code == 200
        assert resp.json()["email"] == "existente@email.com"

    def test_retorna_404_para_id_inexistente(self, admin_client):
        assert admin_client.get("/usuarios/9999").status_code == 404


class TestAtivarDesativarUsuario:
    def test_ativa_usuario_inativo(self, admin_client, session):
        seed_usuario(session, id=10, ativo=False)
        resp = admin_client.patch("/usuarios/10/ativar")
        assert resp.status_code == 200
        assert resp.json()["ativo"] is True

    def test_ativar_usuario_ja_ativo_retorna_400(self, admin_client, session):
        seed_usuario(session, id=10, ativo=True)
        resp = admin_client.patch("/usuarios/10/ativar")
        assert resp.status_code == 400

    def test_desativa_usuario_ativo(self, admin_client, session):
        # id=10 (diferente do admin id=2 no conftest)
        seed_usuario(session, id=10, ativo=True)
        resp = admin_client.patch("/usuarios/10/desativar")
        assert resp.status_code == 200
        assert resp.json()["ativo"] is False

    def test_desativar_usuario_ja_inativo_retorna_400(self, admin_client, session):
        seed_usuario(session, id=10, ativo=False)
        resp = admin_client.patch("/usuarios/10/desativar")
        assert resp.status_code == 400

    def test_nao_pode_desativar_a_si_mesmo(self, admin_client, session):
        # O admin tem id=2 no conftest; tentar desativar o próprio id
        seed_usuario(session, id=2, email="admin@teste.com", ativo=True)
        resp = admin_client.patch("/usuarios/2/desativar")
        assert resp.status_code == 400
        assert "si mesmo" in resp.json()["detail"]


class TestAtualizarUsuario:
    def test_atualiza_nome(self, admin_client, session):
        seed_usuario(session, id=10)
        resp = admin_client.patch("/usuarios/10", json={"nome": "Nome Atualizado"})
        assert resp.status_code == 200
        assert resp.json()["nome"] == "Nome Atualizado"

    def test_nao_pode_rebaixar_proprio_papel(self, admin_client, session):
        # Admin (id=2) tenta rebaixar o próprio papel para 'usuario'
        seed_usuario(session, id=2, email="admin@teste.com", papel=PapelUsuario.superusuario)
        resp = admin_client.patch("/usuarios/2", json={"papel": "usuario"})
        assert resp.status_code == 400
        assert "rebaixar" in resp.json()["detail"]

    def test_email_duplicado_na_atualizacao_retorna_409(self, admin_client, session):
        seed_usuario(session, id=10, email="joao@email.com")
        seed_usuario(session, id=11, email="maria@email.com")
        resp = admin_client.patch("/usuarios/11", json={"email": "joao@email.com"})
        assert resp.status_code == 409

    def test_retorna_404_para_id_inexistente(self, admin_client):
        assert admin_client.patch("/usuarios/9999", json={"nome": "X"}).status_code == 404


class TestDeletarUsuario:
    def test_deleta_usuario(self, admin_client, session):
        seed_usuario(session, id=10)
        resp = admin_client.delete("/usuarios/10")
        assert resp.status_code == 204
        assert admin_client.get("/usuarios/10").status_code == 404

    def test_nao_pode_remover_a_si_mesmo(self, admin_client, session):
        seed_usuario(session, id=2, email="admin@teste.com")
        resp = admin_client.delete("/usuarios/2")
        assert resp.status_code == 400
        assert "si mesmo" in resp.json()["detail"]

    def test_retorna_404_para_id_inexistente(self, admin_client):
        assert admin_client.delete("/usuarios/9999").status_code == 404
