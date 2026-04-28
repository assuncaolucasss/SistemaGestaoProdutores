import re
from pydantic import BaseModel, field_validator, ConfigDict


def validar_senha(senha: str) -> str:
    erros = []
    if len(senha) < 8:
        erros.append("mínimo 8 caracteres")
    if not re.search(r"[A-Z]", senha):
        erros.append("pelo menos 1 letra maiúscula")
    if not re.search(r"[a-z]", senha):
        erros.append("pelo menos 1 letra minúscula")
    if not re.search(r"\d", senha):          # ← era r"\\d" (double escape errado)
        erros.append("pelo menos 1 número")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        erros.append("pelo menos 1 caractere especial (!@#$%...)")
    if erros:
        raise ValueError(f"Senha fraca: {', '.join(erros)}")
    return senha


class SenhaUpdate(BaseModel):
    senha: str

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, v):
        return validar_senha(v)


class RecuperarSenhaRequest(BaseModel):
    email: str


class ConfirmarCodigoRequest(BaseModel):
    email: str
    codigo: str


class RedefinirSenhaRequest(BaseModel):
    email: str
    codigo: str
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def senha_forte(cls, v):
        return validar_senha(v)