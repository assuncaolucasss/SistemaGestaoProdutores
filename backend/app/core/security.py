import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.core.config import settings
from app.models.base import get_session
from app.models.usuario import Usuario, PapelUsuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(
        senha_plana.encode("utf-8"),
        senha_hash.encode("utf-8")
    )


def criar_token(data: dict, expira_em: Optional[int] = None) -> str:
    payload = data.copy()
    expiracao = datetime.utcnow() + timedelta(
        minutes=expira_em or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expiracao})
    # Garante que o papel é serializado como string pura
    if "papel" in payload and hasattr(payload["papel"], "value"):
        payload["papel"] = payload["papel"].value
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if not usuario or not usuario.ativo:
        raise credentials_exception
    return usuario


def requer_superusuario(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.papel != PapelUsuario.superusuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a superusuários"
        )
    return usuario
