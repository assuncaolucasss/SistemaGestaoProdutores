"""
test_routes_formulario.py — Testa GET /formulario/{produtor_id}/{fomento_id}
============================================================================
Esta é a rota mais crítica do sistema: ela agrega produtor, fomento,
submissão mais recente e características (com normalização de JSON).
"""

import pytest
from app.models.produtor import Produtor
from app.models.fomento import Fomento, ModalidadeClasse, ModalidadeSubclasse, CaracteristicaModalidade
from app.models.submissao import Submissao


# ── Helpers de seed ────────────────────────────────────────────────────────────

def seed_base(session):
    produtor = Produtor(
        id=1,
        cpf_beneficiario="111.222.333-44",
        nome_completo="MARIA DA SILVA",
        assentamento="PA CANAÃ",
        lote="L-12",
        ativo=True,
    )
    fomento = Fomento(id=2, nome="CRÉDITO INSTALAÇÃO INCRA", ativo=True)
    session.add(produtor)
    session.add(fomento)
    session.commit()


def seed_hierarquia(session):
    classe = ModalidadeClasse(
        id=10,
        fomento_id=2,
        nome="FOMENTO MULHER",
        escopo="8k",
        ativo=True,
    )
    subclasse = ModalidadeSubclasse(
        id=101,
        fomento_id=2,
        nome="AÇAÍ",
        escopo="8k",
        ativo=True,
    )
    session.add(classe)
    session.add(subclasse)
    session.commit()


def seed_caracteristica(session):
    caract = CaracteristicaModalidade(
        id=1,
        classe_id=10,
        subclasse_id=101,
        justificativa="JUSTIFICATIVA PADRÃO AÇAÍ",
        entidade_elaboracao="EMATER-PA",
        texto_entidade_responsavel="Texto de responsabilidade técnica",
        memoria_calculo=[
            {"discriminacao": "SEMENTE AÇAÍ", "quantidade": 2, "valor_unitario": 250.0, "subtotal": 500.0}
        ],
        mao_obra_especializada=[
            {"descricao": "VISITA TÉCNICA", "visitas": 3, "valor_unitario": 200.0, "subtotal": 600.0}
        ],
    )
    session.add(caract)
    session.commit()


def seed_submissao(session):
    submissao = Submissao(
        id=1,
        produtor_id=1,
        fomento_id=2,
        usuario_id=1,
        modalidade="FOMENTO MULHER",
        numero_processo="PROC-2026-001",
        municipio_data="CANAÃ DOS CARAJÁS",
        data_assinatura="2026-04-01",
    )
    session.add(submissao)
    session.commit()


# ── Cenário 1: sem classe_id / subclasse_id ────────────────────────────────────

class TestFormularioSemCaracteristica:
    def test_retorna_produtor_e_fomento(self, client, session):
        seed_base(session)
        response = client.get("/formulario/1/2")

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["produtor"]["nome_completo"] == "MARIA DA SILVA"
        assert data["produtor"]["assentamento"] == "PA CANAÃ"
        assert data["fomento"]["nome"] == "CRÉDITO INSTALAÇÃO INCRA"

    def test_caracteristica_e_none_sem_query_params(self, client, session):
        seed_base(session)
        data = client.get("/formulario/1/2").json()
        assert data["caracteristica"] is None

    def test_retorna_dados_da_submissao_mais_recente(self, client, session):
        seed_base(session)
        seed_submissao(session)

        data = client.get("/formulario/1/2").json()
        assert data["numero_processo"] == "PROC-2026-001"
        assert data["municipio_data"] == "CANAÃ DOS CARAJÁS"
        assert data["data_assinatura"] == "2026-04-01"

    def test_campos_submissao_sao_none_sem_submissao(self, client, session):
        seed_base(session)
        data = client.get("/formulario/1/2").json()
        assert data["numero_processo"] is None
        assert data["municipio_data"] is None
        assert data["data_assinatura"] is None


# ── Cenário 2: com classe_id e subclasse_id ────────────────────────────────────

class TestFormularioComCaracteristica:
    def setup_full(self, session):
        seed_base(session)
        seed_hierarquia(session)
        seed_caracteristica(session)
        seed_submissao(session)

    def test_retorna_caracteristica_completa(self, client, session):
        self.setup_full(session)
        response = client.get("/formulario/1/2?classe_id=10&subclasse_id=101")

        assert response.status_code == 200, response.text
        caract = response.json()["caracteristica"]
        assert caract is not None
        assert caract["justificativa"] == "JUSTIFICATIVA PADRÃO AÇAÍ"
        assert caract["entidade_elaboracao"] == "EMATER-PA"
        assert caract["texto_entidade_responsavel"] == "Texto de responsabilidade técnica"

    def test_itens_investimento_normalizados(self, client, session):
        self.setup_full(session)
        data = client.get("/formulario/1/2?classe_id=10&subclasse_id=101").json()
        itens = data["caracteristica"]["itens_investimento"]

        assert len(itens) == 1
        assert itens[0]["discriminacao"] == "SEMENTE AÇAÍ"
        assert itens[0]["quantidade"] == 2.0
        assert itens[0]["valor_unitario"] == 250.0
        assert itens[0]["subtotal"] == 500.0

    def test_itens_mao_obra_normalizados(self, client, session):
        self.setup_full(session)
        data = client.get("/formulario/1/2?classe_id=10&subclasse_id=101").json()
        mao_obra = data["caracteristica"]["itens_mao_obra"]

        assert len(mao_obra) == 1
        assert mao_obra[0]["descricao"] == "VISITA TÉCNICA"
        assert mao_obra[0]["visitas"] == 3.0
        assert mao_obra[0]["valor_unitario"] == 200.0
        assert mao_obra[0]["subtotal"] == 600.0

    def test_caracteristica_none_para_combinacao_inexistente(self, client, session):
        seed_base(session)
        seed_hierarquia(session)
        # Sem seed_caracteristica — combinação não existe

        data = client.get("/formulario/1/2?classe_id=10&subclasse_id=101").json()
        assert data["caracteristica"] is None

    def test_retorna_submissao_mais_recente(self, client, session):
        self.setup_full(session)
        # Cria segunda submissão mais recente
        from app.models.submissao import Submissao
        nova = Submissao(
            id=2,
            produtor_id=1,
            fomento_id=2,
            usuario_id=1,
            modalidade="FOMENTO MULHER",
            numero_processo="PROC-2026-002",
        )
        session.add(nova)
        session.commit()

        data = client.get("/formulario/1/2").json()
        assert data["numero_processo"] == "PROC-2026-002"


# ── Cenário 3: erros 404 ───────────────────────────────────────────────────────

class TestFormulario404:
    def test_produtor_inexistente_retorna_404(self, client, session):
        seed_base(session)
        response = client.get("/formulario/9999/2")
        assert response.status_code == 404
        assert "Produtor" in response.json()["detail"]

    def test_fomento_inexistente_retorna_404(self, client, session):
        seed_base(session)
        response = client.get("/formulario/1/9999")
        assert response.status_code == 404
        assert "Fomento" in response.json()["detail"]

    def test_produtor_inativo_retorna_404(self, client, session):
        produtor_inativo = Produtor(
            id=99,
            cpf_beneficiario="000.000.000-00",
            nome_completo="INATIVO",
            ativo=False,
        )
        fomento = Fomento(id=2, nome="CRÉDITO INSTALAÇÃO INCRA", ativo=True)
        session.add(produtor_inativo)
        session.add(fomento)
        session.commit()

        response = client.get("/formulario/99/2")
        assert response.status_code == 404

    def test_fomento_inativo_retorna_404(self, client, session):
        produtor = Produtor(
            id=1, cpf_beneficiario="111.222.333-44",
            nome_completo="MARIA", ativo=True,
        )
        fomento_inativo = Fomento(id=99, nome="FOMENTO INATIVO", ativo=False)
        session.add(produtor)
        session.add(fomento_inativo)
        session.commit()

        response = client.get("/formulario/1/99")
        assert response.status_code == 404
