from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.models.base import get_session
from app.models.submissao import Submissao
from app.schemas.submissao import SubmissaoCreate, SubmissaoUpdate, SubmissaoRead
from app.core.security import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/submissoes", tags=["Submissões"])


@router.post("", response_model=SubmissaoRead)
def criar_submissao(
    dados: SubmissaoCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user)
):
    submissao = Submissao(**dados.model_dump(), usuario_id=usuario.id)
    session.add(submissao)
    session.commit()
    session.refresh(submissao)
    return submissao


@router.get("", response_model=List[SubmissaoRead])
def listar_submissoes(
    produtor_id: Optional[int] = None,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    query = select(Submissao)
    if produtor_id:
        query = query.where(Submissao.produtor_id == produtor_id)
    return session.exec(query).all()


@router.get("/{id}", response_model=SubmissaoRead)
def detalhe_submissao(
    id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    submissao = session.get(Submissao, id)
    if not submissao:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")
    return submissao


@router.patch("/{id}", response_model=SubmissaoRead)
def atualizar_submissao(
    id: int,
    dados: SubmissaoUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    submissao = session.get(Submissao, id)
    if not submissao:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(submissao, campo, valor)

    submissao.atualizado_em = datetime.now()
    session.add(submissao)
    session.commit()
    session.refresh(submissao)
    return submissao


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_submissao(
    id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    submissao = session.get(Submissao, id)
    if not submissao:
        raise HTTPException(status_code=404, detail="Submissão não encontrada")

    session.delete(submissao)
    session.commit()
