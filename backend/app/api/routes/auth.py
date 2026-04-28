from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import random

from app.core.security import verificar_senha, criar_token, get_current_user, hash_senha
from app.models.base import get_session
from app.models.usuario import Usuario
from app.models.codigo_recuperacao import CodigoRecuperacao
from app.services.email import enviar_email_recuperacao

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class EmailSchema(BaseModel):
    email: EmailStr

class VerificarCodigoSchema(BaseModel):
    email: EmailStr
    codigo: str

class NovaSenhaSchema(BaseModel):
    email: EmailStr
    codigo: str
    nova_senha: str


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/token")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    usuario = session.exec(select(Usuario).where(Usuario.email == form.username)).first()

    if not usuario or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    token = criar_token({"sub": usuario.email, "papel": usuario.papel})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(usuario: Usuario = Depends(get_current_user)):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "papel": usuario.papel
    }


# ── Recuperação de senha ──────────────────────────────────────────────────────

@router.post("/recuperar-senha")
def recuperar_senha(data: EmailSchema, session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.email == data.email)).first()

    if not usuario:
        return {"mensagem": "Se o e-mail estiver cadastrado, você receberá o código."}

    # Invalida códigos anteriores
    codigos_anteriores = session.exec(
        select(CodigoRecuperacao).where(
            CodigoRecuperacao.email == data.email,
            CodigoRecuperacao.usado == False
        )
    ).all()
    for c in codigos_anteriores:
        c.usado = True
        session.add(c)

    # Gera novo código
    codigo = str(random.randint(100000, 999999))
    expira_em = datetime.now() + timedelta(minutes=5)

    registro = CodigoRecuperacao(email=data.email, codigo=codigo, expira_em=expira_em)
    session.add(registro)
    session.commit()

    # Envia e-mail
    try:
        enviar_email_recuperacao(data.email, codigo)
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail: {str(e)}")

    return {"mensagem": "Se o e-mail estiver cadastrado, você receberá o código."}


@router.post("/verificar-codigo")
def verificar_codigo(data: VerificarCodigoSchema, session: Session = Depends(get_session)):
    registro = session.exec(
        select(CodigoRecuperacao).where(
            CodigoRecuperacao.email == data.email,
            CodigoRecuperacao.codigo == data.codigo,
            CodigoRecuperacao.usado == False
        )
    ).first()

    if not registro:
        raise HTTPException(status_code=400, detail="Código inválido.")

    if datetime.now() > registro.expira_em:
        raise HTTPException(status_code=400, detail="Código expirado.")

    return {"mensagem": "Código válido."}


@router.post("/nova-senha")
def nova_senha(data: NovaSenhaSchema, session: Session = Depends(get_session)):
    registro = session.exec(
        select(CodigoRecuperacao).where(
            CodigoRecuperacao.email == data.email,
            CodigoRecuperacao.codigo == data.codigo,
            CodigoRecuperacao.usado == False
        )
    ).first()

    if not registro:
        raise HTTPException(status_code=400, detail="Código inválido.")

    if datetime.now() > registro.expira_em:
        raise HTTPException(status_code=400, detail="Código expirado.")

    usuario = session.exec(select(Usuario).where(Usuario.email == data.email)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    usuario.senha_hash = hash_senha(data.nova_senha)
    registro.usado = True

    session.add(usuario)
    session.add(registro)
    session.commit()

    return {"mensagem": "Senha atualizada com sucesso."}