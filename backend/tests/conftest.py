"""
conftest.py — Fixtures globais para o pacote de testes
======================================================
- Banco SQLite em memória, isolado do banco de desenvolvimento
- Sobrescreve get_session, get_current_user e requer_superusuario
- Dois fixtures de client: `client` (usuário normal) e `admin_client` (superusuário)
- JSONB → JSON: SQLite não suporta JSONB (tipo exclusivo do PostgreSQL)
- upper() e LIKE com Unicode: SQLite nativamente só processa ASCII;
  registramos funções Python para suportar caracteres não-ASCII nos testes.
"""

import re
import unicodedata
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy import JSON, event
from sqlalchemy.dialects.postgresql import JSONB

from app.main import app
from app.models.base import get_session
from app.core.security import get_current_user, requer_superusuario
from app.models.usuario import Usuario, PapelUsuario


# ── Engine SQLite em memória ───────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# ── Fix 1: substitui JSONB → JSON no metadata ──────────────────────────────────
def _patch_jsonb_to_json():
    for table in SQLModel.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, JSONB):
                column.type = JSON()

_patch_jsonb_to_json()


# ── Fix 2: funções Unicode para SQLite ────────────────────────────────────────
# O SQLite nativo só faz upper/lower e LIKE case-insensitive para ASCII.
# Registramos funções Python na conexão SQLite para corrigir isso nos testes.

def _normalizar_para_like(texto: str) -> str:
    """Remove acentos e converte para maiúsculas — replica o que a rota faz."""
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8").upper()

def _sqlite_upper(s):
    return s.upper() if s else s

def _sqlite_like(pattern, text):
    """
    Implementa LIKE com suporte a Unicode e remoção de acentos.
    Replica exatamente a lógica de _normalizar() usada na rota de produtores.
    """
    if text is None or pattern is None:
        return False
    # Normaliza ambos os lados exatamente como a rota faz com o termo de busca
    text_norm    = _normalizar_para_like(text)
    pattern_norm = pattern.replace("%", ".*").replace("_", ".")
    return bool(re.fullmatch(pattern_norm, text_norm))

@event.listens_for(engine, "connect")
def _registrar_funcoes_sqlite(dbapi_conn, _):
    dbapi_conn.create_function("upper", 1, _sqlite_upper)
    # like(pattern, string) — chamado pelo SQLite quando upper(col).like(termo)
    dbapi_conn.create_function("like",  2, _sqlite_like)


# ── Overrides de dependências ──────────────────────────────────────────────────
def override_get_session():
    with Session(engine) as session:
        yield session


USUARIO_NORMAL = Usuario(
    id=1,
    nome="Lucas Teste",
    email="lucas@teste.com",
    senha_hash="hashfake",
    papel=PapelUsuario.usuario,
    ativo=True,
)

USUARIO_ADMIN = Usuario(
    id=2,
    nome="Admin Teste",
    email="admin@teste.com",
    senha_hash="hashfake",
    papel=PapelUsuario.superusuario,
    ativo=True,
)


def override_get_current_user():
    return USUARIO_NORMAL


def override_requer_superusuario():
    return USUARIO_ADMIN


# ── Criação/destruição do banco ────────────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def prepare_db():
    """Cria todas as tabelas no início da sessão e derruba no final."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def limpar_tabelas():
    """Limpa todas as tabelas entre cada teste para garantir isolamento."""
    yield
    with Session(engine) as session:
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.exec(table.delete())
        session.commit()


# ── Fixture de Session direta ──────────────────────────────────────────────────
@pytest.fixture
def session():
    """Sessão direta para popular dados de seed nos testes."""
    with Session(engine) as s:
        yield s


# ── Fixtures de TestClient ─────────────────────────────────────────────────────
@pytest.fixture
def client():
    """TestClient autenticado como usuário normal."""
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[requer_superusuario] = override_requer_superusuario
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client():
    """TestClient autenticado como superusuário."""
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_requer_superusuario
    app.dependency_overrides[requer_superusuario] = override_requer_superusuario
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()