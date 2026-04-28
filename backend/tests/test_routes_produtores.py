"""
test_routes_produtores.py — Testa CRUD de /produtores/
"""
import pytest
from app.models.produtor import Produtor

PRODUTOR_BASE = {
    "cpf_beneficiario": "111.222.333-44",
    "nome_completo": "MARIA DA SILVA",
    "assentamento": "PA CANAÃ",
    "lote": "L-12",
}


def seed_dois_produtores(session):
    session.add(Produtor(id=1, cpf_beneficiario="111.222.333-44", nome_completo="MARIA DA SILVA", assentamento="PA CANAÃ", lote="L-12", ativo=True))
    session.add(Produtor(id=2, cpf_beneficiario="999.888.777-66", nome_completo="JOÃO SOUZA", assentamento="PA OUTRO", lote="L-5", ativo=True))
    session.commit()


class TestListarProdutores:
    def test_lista_vazia(self, client):
        assert client.get("/produtores/").json() == []

    def test_lista_produtores_ativos(self, client, session):
        seed_dois_produtores(session)
        resp = client.get("/produtores/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_filtro_busca_por_nome(self, client, session):
        seed_dois_produtores(session)
        resp = client.get("/produtores/?busca=MARIA")
        assert len(resp.json()) == 1
        assert resp.json()[0]["nome_completo"] == "MARIA DA SILVA"

    def test_filtro_busca_por_cpf(self, client, session):
        seed_dois_produtores(session)
        resp = client.get("/produtores/?busca=999.888.777-66")
        assert len(resp.json()) == 1

    def test_filtro_por_assentamento(self, client, session):
        seed_dois_produtores(session)
        resp = client.get("/produtores/?assentamento=PA%20OUTRO")
        assert len(resp.json()) == 1
        assert resp.json()[0]["nome_completo"] == "JOÃO SOUZA"

    def test_paginacao_limit(self, client, session):
        seed_dois_produtores(session)
        resp = client.get("/produtores/?limit=1")
        assert len(resp.json()) == 1

    def test_paginacao_skip(self, client, session):
        seed_dois_produtores(session)
        resp = client.get("/produtores/?skip=1&limit=10")
        assert len(resp.json()) == 1


class TestTotalProdutores:
    def test_total_zero(self, client):
        resp = client.get("/produtores/total")
        assert resp.status_code == 200
        assert resp.json() == 0

    def test_total_correto(self, client, session):
        seed_dois_produtores(session)
        assert client.get("/produtores/total").json() == 2

    def test_total_com_filtro_busca(self, client, session):
        seed_dois_produtores(session)
        assert client.get("/produtores/total?busca=JOAO").json() == 1


class TestDetalheProdutores:
    def test_retorna_produtor_pelo_id(self, client, session):
        seed_dois_produtores(session)
        resp = client.get("/produtores/1")
        assert resp.status_code == 200
        assert resp.json()["nome_completo"] == "MARIA DA SILVA"

    def test_retorna_404_para_id_inexistente(self, client):
        assert client.get("/produtores/9999").status_code == 404


class TestCriarProdutores:
    def test_cria_produtor(self, admin_client):
        resp = admin_client.post("/produtores/", json=PRODUTOR_BASE)
        assert resp.status_code == 200
        assert resp.json()["nome_completo"] == "MARIA DA SILVA"
        assert resp.json()["ativo"] is True


class TestAtualizarProdutores:
    def test_atualiza_campo_simples(self, admin_client, session):
        seed_dois_produtores(session)
        resp = admin_client.patch("/produtores/1", json={"lote": "L-99"})
        assert resp.status_code == 200
        assert resp.json()["lote"] == "L-99"

    def test_retorna_404_para_id_inexistente(self, admin_client):
        assert admin_client.patch("/produtores/9999", json={"lote": "X"}).status_code == 404


class TestDeletarProdutores:
    def test_deleta_produtor(self, admin_client, session):
        seed_dois_produtores(session)
        resp = admin_client.delete("/produtores/1")
        assert resp.status_code == 204
        assert admin_client.get("/produtores/1").status_code == 404

    def test_retorna_404_para_id_inexistente(self, admin_client):
        assert admin_client.delete("/produtores/9999").status_code == 404
