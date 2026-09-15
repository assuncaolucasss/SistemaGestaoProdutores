from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime

from app.models.base import get_session
from app.models.fomento import (
    Fomento, ModalidadeClasse, ModalidadeSubclasse, CaracteristicaModalidade
)
from app.schemas.fomento import (
    FomentoCreate, FomentoUpdate, FomentoRead,
    ModalidadeClasseCreate, ModalidadeClasseUpdate, ModalidadeClasseRead,
    ModalidadeSubclasseCreate, ModalidadeSubclasseUpdate, ModalidadeSubclasseRead,
    CaracteristicaCreate, CaracteristicaUpdate, CaracteristicaRead,
    HierarquiaFomentoRead, ClasseComSubclasses, SubclasseComCaracteristica,
)
from app.core.security import get_current_user, requer_superusuario
from app.models.usuario import Usuario

router = APIRouter(prefix="/fomentos", tags=["Fomentos"])


# ══════════════════════════════════════════════════════
# ROTAS FIXAS — devem vir ANTES das rotas com {id}
# ══════════════════════════════════════════════════════

@router.get("/", response_model=List[FomentoRead])
def listar_fomentos(
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    return session.exec(select(Fomento).where(Fomento.ativo == True)).all()


@router.post("/", response_model=FomentoRead, status_code=201)
def criar_fomento(
    dados: FomentoCreate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    fomento = Fomento(**dados.model_dump())
    session.add(fomento)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        # Extrai o erro real disparado pelo PostgreSQL para debug no Frontend
        erro_banco = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        raise HTTPException(
            status_code=409, 
            detail=f"Falha no Banco de Dados: {erro_banco}"
        )
    session.refresh(fomento)
    return fomento


# ── Características — rotas fixas com prefixo literal ─
# CRÍTICO: estas rotas devem vir ANTES de /{id} e /{fomento_id}/...
# Se vierem depois, o FastAPI interpreta "caracteristicas" como o valor de {id}

@router.get("/caracteristicas/{classe_id}/{subclasse_id}", response_model=CaracteristicaRead)
def buscar_caracteristica(
    classe_id: int,
    subclasse_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    caract = session.exec(
        select(CaracteristicaModalidade)
        .where(
            CaracteristicaModalidade.classe_id == classe_id,
            CaracteristicaModalidade.subclasse_id == subclasse_id,
        )
    ).first()
    if not caract:
        raise HTTPException(status_code=404, detail="Características não cadastradas para esta combinação")
    return caract


@router.post("/caracteristicas", response_model=CaracteristicaRead, status_code=201)
def criar_caracteristica(
    dados: CaracteristicaCreate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    existente = session.exec(
        select(CaracteristicaModalidade)
        .where(
            CaracteristicaModalidade.classe_id == dados.classe_id,
            CaracteristicaModalidade.subclasse_id == dados.subclasse_id,
        )
    ).first()
    if existente:
        raise HTTPException(
            status_code=409,
            detail="Já existe uma característica para esta combinação. Use PATCH para atualizar."
        )
    caract = CaracteristicaModalidade(**dados.model_dump())
    session.add(caract)
    session.commit()
    session.refresh(caract)
    return caract


@router.patch("/caracteristicas/{id}", response_model=CaracteristicaRead)
def atualizar_caracteristica(
    id: int,
    dados: CaracteristicaUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    caract = session.get(CaracteristicaModalidade, id)
    if not caract:
        raise HTTPException(status_code=404, detail="Característica não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(caract, campo, valor)
    caract.atualizado_em = datetime.now()
    session.add(caract)
    session.commit()
    session.refresh(caract)
    return caract


# ── Classes — rotas fixas com prefixo literal ─────────
# Também devem vir ANTES de /{id}

@router.patch("/classes/{classe_id}", response_model=ModalidadeClasseRead)
def atualizar_classe(
    classe_id: int,
    dados: ModalidadeClasseUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    classe = session.get(ModalidadeClasse, classe_id)
    if not classe:
        raise HTTPException(status_code=404, detail="Classe não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(classe, campo, valor)
    session.add(classe)
    session.commit()
    session.refresh(classe)
    return classe


@router.delete("/classes/{classe_id}", status_code=204)
def deletar_classe(
    classe_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    """Exclui fisicamente a classe e suas características associadas."""
    classe = session.get(ModalidadeClasse, classe_id)
    if not classe:
        raise HTTPException(status_code=404, detail="Classe não encontrada")
    
    try:
        caracteristicas = session.exec(
            select(CaracteristicaModalidade).where(CaracteristicaModalidade.classe_id == classe.id)
        ).all()
        for c in caracteristicas:
            session.delete(c)
            
        session.flush()
        session.delete(classe)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Registros relacionados impedem a exclusão.") from exc


# ── Subclasses — rotas fixas com prefixo literal ──────

@router.patch("/subclasses/{subclasse_id}", response_model=ModalidadeSubclasseRead)
def atualizar_subclasse(
    subclasse_id: int,
    dados: ModalidadeSubclasseUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    sub = session.get(ModalidadeSubclasse, subclasse_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subclasse não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(sub, campo, valor)
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub


@router.delete("/subclasses/{subclasse_id}", status_code=204)
def deletar_subclasse(
    subclasse_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    """Exclui fisicamente a subclasse e suas características associadas."""
    sub = session.get(ModalidadeSubclasse, subclasse_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subclasse não encontrada")
    
    try:
        caracteristicas = session.exec(
            select(CaracteristicaModalidade).where(CaracteristicaModalidade.subclasse_id == sub.id)
        ).all()
        for c in caracteristicas:
            session.delete(c)
            
        session.flush()
        session.delete(sub)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Registros relacionados impedem a exclusão.") from exc


# ══════════════════════════════════════════════════════
# ROTAS COM PARÂMETRO DINÂMICO {id} — vêm POR ÚLTIMO
# ══════════════════════════════════════════════════════

@router.get("/{id}", response_model=FomentoRead)
def detalhe_fomento(
    id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    fomento = session.get(Fomento, id)
    if not fomento:
        raise HTTPException(status_code=404, detail="Fomento não encontrado")
    return fomento


@router.patch("/{id}", response_model=FomentoRead)
def atualizar_fomento(
    id: int,
    dados: FomentoUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    fomento = session.get(Fomento, id)
    if not fomento:
        raise HTTPException(status_code=404, detail="Fomento não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(fomento, campo, valor)
    session.add(fomento)
    session.commit()
    session.refresh(fomento)
    return fomento


@router.delete("/{id}", status_code=204)
def deletar_fomento(
    id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    """Exclui fisicamente um fomento e todos os seus dados associados em cascata."""
    fomento = session.get(Fomento, id)
    if not fomento:
        raise HTTPException(status_code=404, detail="Fomento não encontrado")

    try:
        classes = session.exec(
            select(ModalidadeClasse).where(ModalidadeClasse.fomento_id == id)
        ).all()
        subclasses = session.exec(
            select(ModalidadeSubclasse).where(ModalidadeSubclasse.fomento_id == id)
        ).all()

        caracteristicas_para_deletar = {}
        
        if classes:
            caract_classes = session.exec(
                select(CaracteristicaModalidade).where(
                    CaracteristicaModalidade.classe_id.in_([c.id for c in classes])
                )
            ).all()
            for c in caract_classes:
                caracteristicas_para_deletar[c.id] = c
                
        if subclasses:
            caract_subs = session.exec(
                select(CaracteristicaModalidade).where(
                    CaracteristicaModalidade.subclasse_id.in_([s.id for s in subclasses])
                )
            ).all()
            for c in caract_subs:
                caracteristicas_para_deletar[c.id] = c

        for caract in caracteristicas_para_deletar.values():
            session.delete(caract)
            
        session.flush() 

        for sub in subclasses:
            session.delete(sub)
            
        session.flush() 

        for classe in classes:
            session.delete(classe)
            
        session.flush() 

        session.delete(fomento)
        session.commit()

    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Não foi possível remover o fomento porque ainda existem registros relacionados em outra tabela."
        ) from exc


@router.get("/{id}/hierarquia", response_model=HierarquiaFomentoRead)
def hierarquia_fomento(
    id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    fomento = session.get(Fomento, id)
    if not fomento:
        raise HTTPException(status_code=404, detail="Fomento não encontrado")

    classes = session.exec(
        select(ModalidadeClasse)
        .where(ModalidadeClasse.fomento_id == id, ModalidadeClasse.ativo == True)
    ).all()

    resultado: List[ClasseComSubclasses] = []

    for classe in classes:
        subclasses = session.exec(
            select(ModalidadeSubclasse)
            .where(
                ModalidadeSubclasse.fomento_id == id,
                ModalidadeSubclasse.escopo == classe.escopo,
                ModalidadeSubclasse.ativo == True,
            )
        ).all()

        itens: List[SubclasseComCaracteristica] = []
        for sub in subclasses:
            caract = session.exec(
                select(CaracteristicaModalidade)
                .where(
                    CaracteristicaModalidade.classe_id == classe.id,
                    CaracteristicaModalidade.subclasse_id == sub.id,
                )
            ).first()
            itens.append(SubclasseComCaracteristica(subclasse=sub, caracteristica=caract))

        resultado.append(ClasseComSubclasses(classe=classe, subclasses=itens))

    return HierarquiaFomentoRead(fomento=fomento, hierarquia=resultado)


@router.get("/{fomento_id}/classes", response_model=List[ModalidadeClasseRead])
def listar_classes(
    fomento_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    return session.exec(
        select(ModalidadeClasse)
        .where(ModalidadeClasse.fomento_id == fomento_id, ModalidadeClasse.ativo == True)
    ).all()


@router.post("/{fomento_id}/classes", response_model=ModalidadeClasseRead, status_code=201)
def criar_classe(
    fomento_id: int,
    dados: ModalidadeClasseCreate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    if not session.get(Fomento, fomento_id):
        raise HTTPException(status_code=404, detail="Fomento não encontrado")
    if dados.escopo not in ("8k", "16k"):
        raise HTTPException(status_code=422, detail="escopo deve ser '8k' ou '16k'")
    classe = ModalidadeClasse(**dados.model_dump())
    session.add(classe)
    session.commit()
    session.refresh(classe)
    return classe


@router.get("/{fomento_id}/subclasses", response_model=List[ModalidadeSubclasseRead])
def listar_subclasses(
    fomento_id: int,
    escopo: str = "8k",
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    return session.exec(
        select(ModalidadeSubclasse)
        .where(
            ModalidadeSubclasse.fomento_id == fomento_id,
            ModalidadeSubclasse.escopo == escopo,
            ModalidadeSubclasse.ativo == True,
        )
    ).all()


@router.post("/{fomento_id}/subclasses", response_model=ModalidadeSubclasseRead, status_code=201)
def criar_subclasse(
    fomento_id: int,
    dados: ModalidadeSubclasseCreate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario)
):
    if not session.get(Fomento, fomento_id):
        raise HTTPException(status_code=404, detail="Fomento não encontrado")
    if dados.escopo not in ("8k", "16k"):
        raise HTTPException(status_code=422, detail="escopo deve ser '8k' ou '16k'")
    subclasse = ModalidadeSubclasse(**dados.model_dump())
    session.add(subclasse)
    session.commit()
    session.refresh(subclasse)
    return subclasse
