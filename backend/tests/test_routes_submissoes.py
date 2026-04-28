"""
test_routes_submissoes.py — Testa CRUD de /submissoes/
======================================================
Cobre criação, listagem com filtro, detalhe, update e delete.
O usuario_id é injetado pelo backend a partir do usuário autenticado (id=1 no conftest).
"""

import pytest
from app.models.produtor import Produtor
from app.models.fomento import Fomento


# ── Helpers de seed ────────────────────────────────────────────────────────────

def seed_produtor_fomento(session):
    produtor = Produtor(
        id=10,
        cpf_beneficiario="111.222.333-44",
        nome_completo="MARIA DA SILVA",
        ativo=True,
    )
    fomento = Fomento(
        id=20,
        nome="CRÉDITO INSTALAÇÃO INCRA",
        ativo=True,
    )
    session.add(produtor)
    session.add(fomento)
    session.commit()


PAYLOAD_BASE = {
    "fomento_id": 20,
    "produtor_id": 10,
    "modalidade": "FOMENTO MULHER",
}


# ── POST /submissoes/ ──────────────────────────────────────────────────────────

class TestCriarSubmissao:
    def test_cria_submissao_minima(self, client, session):
        seed_produtor_fomento(session)
        response = client.post("/submissoes/", json=PAYLOAD_BASE)

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["fomento_id"] == 20
        assert data["produtor_id"] == 10
        # usuario_id deve vir do usuário autenticado (id=1 no conftest)
        assert data["usuario_id"] == 1
        assert data["modalidade"] == "FOMENTO MULHER"

    def test_cria_submissao_com_todos_os_campos(self, client, session):
        seed_produtor_fomento(session)
        payload = {
            **PAYLOAD_BASE,
            "numero_processo":            "PROC-2026-001",
            "classe_id":                  None,
            "subclasse_id":               None,
            "justificativa":              "Justificativa de teste",
            "entidade_elaboracao":        "EMATER",
            "texto_entidade_responsavel": "Texto responsável",
            "municipio_data":             "CANAÃ DOS CARAJÁS",
            "data_assinatura":            "2026-04-27",
            "itens_investimento": [
                {"discriminacao": "SEMENTE AÇAÍ", "quantidade": 2, "valor_unitario": 250.0, "subtotal": 500.0}
            ],
            "itens_mao_obra": [
                {"descricao": "VISITA TÉCNICA", "visitas": 3.0, "valor_unitario": 200.0, "subtotal": 600.0}
            ],
        }
        response = client.post("/submissoes/", json=payload)
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["numero_processo"] == "PROC-2026-001"
        assert data["entidade_elaboracao"] == "EMATER"
        assert data["municipio_data"] == "CANAÃ DOS CARAJÁS"
        assert len(data["itens_investimento"]) == 1
        assert len(data["itens_mao_obra"]) == 1

    def test_rejeita_sem_fomento_id(self, client, session):
        seed_produtor_fomento(session)
        payload = {"produtor_id": 10, "modalidade": "FOMENTO MULHER"}
        response = client.post("/submissoes/", json=payload)
        assert response.status_code == 422

    def test_rejeita_sem_produtor_id(self, client, session):
        seed_produtor_fomento(session)
        payload = {"fomento_id": 20, "modalidade": "FOMENTO MULHER"}
        response = client.post("/submissoes/", json=payload)
        assert response.status_code == 422

    def test_rejeita_sem_modalidade(self, client, session):
        seed_produtor_fomento(session)
        payload = {"fomento_id": 20, "produtor_id": 10}
        response = client.post("/submissoes/", json=payload)
        assert response.status_code == 422


# ── GET /submissoes/ ───────────────────────────────────────────────────────────

class TestListarSubmissoes:
    def test_lista_vazia_inicialmente(self, client):
        response = client.get("/submissoes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_lista_submissoes_criadas(self, client, session):
        seed_produtor_fomento(session)
        client.post("/submissoes/", json=PAYLOAD_BASE)
        client.post("/submissoes/", json=PAYLOAD_BASE)

        response = client.get("/submissoes/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_filtra_por_produtor_id(self, client, session):
        # Cria dois produtores
        session.add(Produtor(id=10, cpf_beneficiario="111.222.333-44", nome_completo="MARIA", ativo=True))
        session.add(Produtor(id=11, cpf_beneficiario="999.888.777-66", nome_completo="JOÃO", ativo=True))
        session.add(Fomento(id=20, nome="CRÉDITO INSTALAÇÃO INCRA", ativo=True))
        session.commit()

        client.post("/submissoes/", json={**PAYLOAD_BASE, "produtor_id": 10})
        client.post("/submissoes/", json={**PAYLOAD_BASE, "produtor_id": 11})

        response = client.get("/submissoes/?produtor_id=10")
        assert response.status_code == 200
        dados = response.json()
        assert len(dados) == 1
        assert dados[0]["produtor_id"] == 10


# ── GET /submissoes/{id} ───────────────────────────────────────────────────────

class TestDetalheSubmissao:
    def test_retorna_submissao_existente(self, client, session):
        seed_produtor_fomento(session)
        criado = client.post("/submissoes/", json=PAYLOAD_BASE).json()

        response = client.get(f"/submissoes/{criado['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == criado["id"]

    def test_retorna_404_para_id_inexistente(self, client):
        response = client.get("/submissoes/9999")
        assert response.status_code == 404


# ── PATCH /submissoes/{id} ─────────────────────────────────────────────────────

class TestAtualizarSubmissao:
    def test_atualiza_campos_opcionais(self, client, session):
        seed_produtor_fomento(session)
        criado = client.post("/submissoes/", json=PAYLOAD_BASE).json()

        response = client.patch(f"/submissoes/{criado['id']}", json={
            "numero_processo": "PROC-ATUALIZADO",
            "municipio_data":  "PARAUAPEBAS",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["numero_processo"] == "PROC-ATUALIZADO"
        assert data["municipio_data"] == "PARAUAPEBAS"

    def test_retorna_404_para_id_inexistente(self, client):
        response = client.patch("/submissoes/9999", json={"modalidade": "X"})
        assert response.status_code == 404


# ── DELETE /submissoes/{id} ────────────────────────────────────────────────────

class TestDeletarSubmissao:
    def test_deleta_submissao_existente(self, client, session):
        seed_produtor_fomento(session)
        criado = client.post("/submissoes/", json=PAYLOAD_BASE).json()

        response = client.delete(f"/submissoes/{criado['id']}")
        assert response.status_code == 204

        # Confirma que sumiu
        assert client.get(f"/submissoes/{criado['id']}").status_code == 404

    def test_retorna_404_para_id_inexistente(self, client):
        response = client.delete("/submissoes/9999")
        assert response.status_code == 404
