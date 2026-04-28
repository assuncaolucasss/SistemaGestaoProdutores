"""
test_main.py — Testa o exception handler customizado de validação (422)
=======================================================================
O main.py sobrescreve o handler padrão do FastAPI para RequestValidationError,
retornando { "detail": "Erro de validação", "erros": [...] }.
"""


def test_handler_422_formato_customizado(client):
    """
    POST /submissoes/ sem body deve disparar 422 com o formato customizado.
    O handler transforma cada erro em { campo, mensagem }.
    """
    response = client.post("/submissoes/", json={})

    assert response.status_code == 422

    data = response.json()
    assert data["detail"] == "Erro de validação", (
        "O handler customizado deve retornar detail='Erro de validação'"
    )
    assert "erros" in data, "A resposta deve conter a chave 'erros'"
    assert isinstance(data["erros"], list), "'erros' deve ser uma lista"
    assert len(data["erros"]) > 0, "Deve haver ao menos um erro de validação"


def test_handler_422_campos_dos_erros(client):
    """Cada item de 'erros' deve ter as chaves 'campo' e 'mensagem'."""
    response = client.post("/submissoes/", json={})
    erros = response.json()["erros"]

    for erro in erros:
        assert "campo" in erro, f"Erro sem chave 'campo': {erro}"
        assert "mensagem" in erro, f"Erro sem chave 'mensagem': {erro}"


def test_handler_422_nao_expoe_detalhe_raw(client):
    """
    O handler remove o prefixo 'Value error, ' das mensagens pydantic.
    Garante que mensagens customizadas chegam limpas ao frontend.
    """
    response = client.post("/submissoes/", json={})
    erros = response.json()["erros"]

    for erro in erros:
        assert not erro["mensagem"].startswith("Value error, "), (
            f"Mensagem não foi limpa: {erro['mensagem']}"
        )
