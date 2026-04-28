"""
test_routes_fomentos.py — Testa CRUD de /fomentos/ e rotas de hierarquia
"""
import pytest
from app.models.fomento import Fomento, ModalidadeClasse, ModalidadeSubclasse, CaracteristicaModalidade


def seed_fomento(session):
    session.add(Fomento(id=1, nome="CRÉDITO INSTALAÇÃO INCRA", ativo=True))
    session.commit()


def seed_hierarquia(session):
    session.add(ModalidadeClasse(id=10, fomento_id=1, nome="FOMENTO MULHER", escopo="8k", ativo=True))
    session.add(ModalidadeSubclasse(id=101, fomento_id=1, nome="AÇAÍ", escopo="8k", ativo=True))
    session.commit()


class TestListarFomentos:
    def test_lista_vazia(self, client):
        assert client.get("/fomentos/").json() == []

    def test_lista_fomentos_ativos(self, client, session):
        seed_fomento(session)
        resp = client.get("/fomentos/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_nao_lista_fomentos_inativos(self, client, session):
        session.add(Fomento(id=2, nome="INATIVO", ativo=False))
        session.commit()
        assert client.get("/fomentos/").json() == []


class TestCriarFomento:
    def test_cria_fomento(self, admin_client):
        resp = admin_client.post("/fomentos/", json={"nome": "NOVO FOMENTO"})
        assert resp.status_code == 201
        assert resp.json()["nome"] == "NOVO FOMENTO"

    def test_nome_duplicado_retorna_409(self, admin_client, session):
        seed_fomento(session)
        resp = admin_client.post("/fomentos/", json={"nome": "CRÉDITO INSTALAÇÃO INCRA"})
        assert resp.status_code == 409


class TestCaracteristicas:
    def test_busca_caracteristica_existente(self, client, session):
        seed_fomento(session)
        seed_hierarquia(session)
        session.add(CaracteristicaModalidade(
            id=1, classe_id=10, subclasse_id=101,
            justificativa="JUSTIFICATIVA", memoria_calculo=[], mao_obra_especializada=[]
        ))
        session.commit()
        resp = client.get("/fomentos/caracteristicas/10/101")
        assert resp.status_code == 200
        assert resp.json()["justificativa"] == "JUSTIFICATIVA"

    def test_caracteristica_inexistente_retorna_404(self, client, session):
        seed_fomento(session)
        seed_hierarquia(session)
        assert client.get("/fomentos/caracteristicas/10/101").status_code == 404

    def test_criar_caracteristica(self, admin_client, session):
        seed_fomento(session)
        seed_hierarquia(session)
        payload = {
            "classe_id": 10, "subclasse_id": 101,
            "justificativa": "NOVA", "memoria_calculo": [], "mao_obra_especializada": []
        }
        resp = admin_client.post("/fomentos/caracteristicas", json=payload)
        assert resp.status_code == 201
        assert resp.json()["justificativa"] == "NOVA"

    def test_criar_caracteristica_duplicada_retorna_409(self, admin_client, session):
        seed_fomento(session)
        seed_hierarquia(session)
        session.add(CaracteristicaModalidade(
            id=1, classe_id=10, subclasse_id=101,
            justificativa="EXISTENTE", memoria_calculo=[], mao_obra_especializada=[]
        ))
        session.commit()
        payload = {
            "classe_id": 10, "subclasse_id": 101,
            "justificativa": "NOVA", "memoria_calculo": [], "mao_obra_especializada": []
        }
        assert admin_client.post("/fomentos/caracteristicas", json=payload).status_code == 409

    def test_atualizar_caracteristica(self, admin_client, session):
        seed_fomento(session)
        seed_hierarquia(session)
        session.add(CaracteristicaModalidade(
            id=1, classe_id=10, subclasse_id=101,
            justificativa="ANTIGA", memoria_calculo=[], mao_obra_especializada=[]
        ))
        session.commit()
        resp = admin_client.patch("/fomentos/caracteristicas/1", json={"justificativa": "ATUALIZADA"})
        assert resp.status_code == 200
        assert resp.json()["justificativa"] == "ATUALIZADA"


class TestHierarquia:
    def test_retorna_hierarquia_completa(self, client, session):
        seed_fomento(session)
        seed_hierarquia(session)
        resp = client.get("/fomentos/1/hierarquia")
        assert resp.status_code == 200
        data = resp.json()
        assert data["fomento"]["nome"] == "CRÉDITO INSTALAÇÃO INCRA"
        assert len(data["hierarquia"]) == 1

    def test_hierarquia_fomento_inexistente_retorna_404(self, client):
        assert client.get("/fomentos/9999/hierarquia").status_code == 404

    def test_listar_classes_do_fomento(self, client, session):
        seed_fomento(session)
        seed_hierarquia(session)
        resp = client.get("/fomentos/1/classes")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_listar_subclasses_por_escopo(self, client, session):
        seed_fomento(session)
        seed_hierarquia(session)
        session.add(ModalidadeSubclasse(id=200, fomento_id=1, nome="PECUÁRIA", escopo="16k", ativo=True))
        session.commit()
        resp_8k = client.get("/fomentos/1/subclasses?escopo=8k")
        resp_16k = client.get("/fomentos/1/subclasses?escopo=16k")
        assert len(resp_8k.json()) == 1
        assert len(resp_16k.json()) == 1
