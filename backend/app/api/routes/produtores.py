import unicodedata
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import datetime

from app.models.base import get_session
from app.models.produtor import Produtor
from app.schemas.produtor import ProdutorRead, ProdutorUpdate
from app.core.security import get_current_user, requer_superusuario
from app.models.usuario import Usuario

router = APIRouter(prefix="/produtores", tags=["Produtores"])


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8").upper()


def _aplicar_filtros(query, busca: Optional[str], assentamento: Optional[str]):
    query = query.where(Produtor.ativo == True)
    if busca:
        termo = f"%{busca.upper()}%"
        termo_normalizado = f"%{_normalizar(busca)}%"
        query = query.where(
            func.upper(Produtor.nome_completo).like(termo)
            | func.upper(Produtor.nome_completo).like(termo_normalizado)
            | func.upper(Produtor.cpf_beneficiario).like(termo)
            | func.upper(Produtor.lote).like(termo)
            | func.upper(Produtor.assentamento).like(termo)
            | func.upper(Produtor.codigo_beneficiario).like(termo)
        )
    if assentamento:
        query = query.where(
            func.upper(Produtor.assentamento) == assentamento.upper()
        )
    return query


@router.get("/total", response_model=int)
def total_produtores(
    busca: Optional[str] = Query(None),
    assentamento: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    query = _aplicar_filtros(select(func.count(Produtor.id)), busca, assentamento)
    return session.exec(query).one()


@router.get("/", response_model=List[ProdutorRead])
def listar_produtores(
    busca: Optional[str] = Query(None),
    assentamento: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(15, le=100),
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    query = _aplicar_filtros(select(Produtor), busca, assentamento)
    query = query.offset(skip).limit(limit)
    return session.exec(query).all()


@router.get("/{id}", response_model=ProdutorRead)
def detalhe_produtor(
    id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    produtor = session.get(Produtor, id)
    if not produtor:
        raise HTTPException(status_code=404, detail="Produtor não encontrado")
    return produtor


@router.post("/", response_model=ProdutorRead)
def criar_produtor(
    dados: ProdutorUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    produtor = Produtor(**dados.model_dump(exclude_unset=True), ativo=True)
    session.add(produtor)
    session.commit()
    session.refresh(produtor)
    return produtor


@router.patch("/{id}", response_model=ProdutorRead)
def atualizar_produtor(
    id: int,
    dados: ProdutorUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    produtor = session.get(Produtor, id)
    if not produtor:
        raise HTTPException(status_code=404, detail="Produtor não encontrado")

    campos_validos = set(Produtor.model_fields.keys())
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        if campo in campos_validos:
            setattr(produtor, campo, valor)

    produtor.atualizado_em = datetime.now()
    session.add(produtor)
    session.commit()
    session.refresh(produtor)
    return produtor


@router.delete("/{id}", status_code=204)
def remover_produtor(
    id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    produtor = session.get(Produtor, id)
    if not produtor:
        raise HTTPException(status_code=404, detail="Produtor não encontrado")
    session.delete(produtor)
    session.commit()
