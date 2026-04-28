# app/api/routes/usuarios.py

import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict

from app.models.base import get_session
from app.models.usuario import Usuario, PapelUsuario
from app.core.security import get_current_user, requer_superusuario, hash_senha


router = APIRouter(prefix="/usuarios", tags=["Usuários"])


# ── Validação de senha segura ─────────────────────────────────────────────────

def validar_senha_forte(senha: str) -> str:
    erros = []
    if len(senha) < 8:
        erros.append("mínimo 8 caracteres")
    if not re.search(r"[A-Z]", senha):
        erros.append("pelo menos 1 letra maiúscula")
    if not re.search(r"[a-z]", senha):
        erros.append("pelo menos 1 letra minúscula")
    if not re.search(r"\d", senha):
        erros.append("pelo menos 1 número")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+]", senha):
        erros.append("pelo menos 1 caractere especial (!@#$%...)")
    if erros:
        raise ValueError(f"Senha fraca: {', '.join(erros)}")
    return senha


# ── Schemas ───────────────────────────────────────────────────────────────────

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    papel: PapelUsuario = PapelUsuario.usuario
    ativo: bool = True

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, v):
        return validar_senha_forte(v)


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    papel: Optional[PapelUsuario] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = None

    @field_validator("senha", mode="before")
    @classmethod
    def senha_forte(cls, v):
        if v is None or v == "":
            return v
        return validar_senha_forte(v)


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    papel: PapelUsuario
    ativo: bool
    criado_em: datetime


# ── Rotas ─────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[UsuarioRead])
def listar_usuarios(
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    return session.exec(select(Usuario)).all()


@router.get("/me", response_model=UsuarioRead)
def meu_perfil(
    current_user: Usuario = Depends(get_current_user),
):
    return current_user


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    data: UsuarioCreate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    existente = session.exec(
        select(Usuario).where(Usuario.email == data.email)
    ).first()
    if existente:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    usuario = Usuario(
        nome=data.nome,
        email=data.email,
        senha_hash=hash_senha(data.senha),
        papel=data.papel,
        ativo=data.ativo,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/ativar", response_model=UsuarioRead)
def ativar_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if usuario.ativo:
        raise HTTPException(status_code=400, detail="Usuário já está ativo")

    usuario.ativo = True
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/desativar", response_model=UsuarioRead)
def desativar_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(requer_superusuario),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode desativar a si mesmo")
    if not usuario.ativo:
        raise HTTPException(status_code=400, detail="Usuário já está inativo")

    usuario.ativo = False
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioRead)
def detalhe_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.patch("/{usuario_id}", response_model=UsuarioRead)
def atualizar_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(requer_superusuario),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if usuario.id == current_user.id and data.papel and data.papel != PapelUsuario.superusuario:
        raise HTTPException(status_code=400, detail="Você não pode rebaixar seu próprio papel")

    if data.email and data.email != usuario.email:
        existente = session.exec(
            select(Usuario).where(Usuario.email == data.email)
        ).first()
        if existente:
            raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        if campo == "senha" and valor:
            setattr(usuario, "senha_hash", hash_senha(valor))
        elif campo != "senha":
            setattr(usuario, campo, valor)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_usuario_permanente(
    usuario_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(requer_superusuario),
):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode remover a si mesmo")

    session.delete(usuario)
    session.commit()
