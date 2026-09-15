from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime

from app.models.base import get_session
from app.models.fomento import (
    Fomento,
    ModalidadeClasse,
    ModalidadeSubclasse,
    CaracteristicaModalidade,
)
from app.schemas.fomento import (
    FomentoCreate,
    FomentoUpdate,
    FomentoRead,
    ModalidadeClasseCreate,
    ModalidadeClasseUpdate,
    ModalidadeClasseRead,
    ModalidadeSubclasseCreate,
    ModalidadeSubclasseUpdate,
    ModalidadeSubclasseRead,
    CaracteristicaCreate,
    CaracteristicaUpdate,
    CaracteristicaRead,
    HierarquiaFomentoRead,
    ClasseComSubclasses,
    SubclasseComCaracteristica,
)
from app.core.security import get_current_user, requer_superusuario
from app.models.usuario import Usuario

router = APIRouter(prefix="/fomentos", tags=["Fomentos"])


def _commit(session: Session, mensagem: str = "Erro ao salvar os dados"):
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail=mensagem) from exc


@router.get("/", response_model=List[FomentoRead])
def listar_fomentos(
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user),
):
    return session.exec(
        select(Fomento).where(Fomento.ativo == True).order_by(Fomento.nome)
    ).all()


@router.post("/", response_model=FomentoRead, status_code=201)
def criar_fomento(
    dados: FomentoCreate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    fomento = Fomento(**dados.model_dump())
    session.add(fomento)
    _commit(session, f"Já existe um fomento com o nome '{dados.nome}'")
    session.refresh(fomento)
    return fomento


@router.get("/caracteristicas/{classe_id}/{subclasse_id}", response_model=CaracteristicaRead)
def buscar_caracteristica(
    classe_id: int,
    subclasse_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user),
):
    caract = session.exec(
        select(CaracteristicaModalidade).where(
            CaracteristicaModalidade.classe_id == classe_id,
            CaracteristicaModalidade.subclasse_id == subclasse_id,
        )
    ).first()
    if not caract:
        raise HTTPException(404, "Características não cadastradas para esta combinação")
    return caract


@router.post("/caracteristicas", response_model=CaracteristicaRead, status_code=201)
def criar_caracteristica(
    dados: CaracteristicaCreate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    existente = session.exec(
        select(CaracteristicaModalidade).where(
            CaracteristicaModalidade.classe_id == dados.classe_id,
            CaracteristicaModalidade.subclasse_id == dados.subclasse_id,
        )
    ).first()
    if existente:
        raise HTTPException(409, "Já existe uma característica para esta combinação. Use PATCH.")
    caract = CaracteristicaModalidade(**dados.model_dump())
    session.add(caract)
    _commit(session)
    session.refresh(caract)
    return caract


@router.patch("/caracteristicas/{id}", response_model=CaracteristicaRead)
def atualizar_caracteristica(
    id: int,
    dados: CaracteristicaUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    caract = session.get(CaracteristicaModalidade, id)
    if not caract:
        raise HTTPException(404, "Característica não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(caract, campo, valor)
    caract.atualizado_em = datetime.now()
    session.add(caract)
    _commit(session)
    session.refresh(caract)
    return caract


@router.patch("/classes/{classe_id}", response_model=ModalidadeClasseRead)
def atualizar_classe(
    classe_id: int,
    dados: ModalidadeClasseUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    classe = session.get(ModalidadeClasse, classe_id)
    if not classe:
        raise HTTPException(404, "Classe não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(classe, campo, valor)
    session.add(classe)
    _commit(session)
    session.refresh(classe)
    return classe


@router.delete("/classes/{classe_id}", status_code=204)
def deletar_classe(
    classe_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    classe = session.get(ModalidadeClasse, classe_id)
    if not classe:
        raise HTTPException(404, "Classe não encontrada")
    classe.ativo = False
    session.add(classe)
    _commit(session)


@router.patch("/subclasses/{subclasse_id}", response_model=ModalidadeSubclasseRead)
def atualizar_subclasse(
    subclasse_id: int,
    dados: ModalidadeSubclasseUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    sub = session.get(ModalidadeSubclasse, subclasse_id)
    if not sub:
        raise HTTPException(404, "Subclasse não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(sub, campo, valor)
    session.add(sub)
    _commit(session)
    session.refresh(sub)
    return sub


@router.delete("/subclasses/{subclasse_id}", status_code=204)
def deletar_subclasse(
    subclasse_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    sub = session.get(ModalidadeSubclasse, subclasse_id)
    if not sub:
        raise HTTPException(404, "Subclasse não encontrada")
    sub.ativo = False
    session.add(sub)
    _commit(session)


@router.get("/{id}", response_model=FomentoRead)
def detalhe_fomento(
    id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user),
):
    fomento = session.get(Fomento, id)
    if not fomento:
        raise HTTPException(404, "Fomento não encontrado")
    return fomento


@router.patch("/{id}", response_model=FomentoRead)
def atualizar_fomento(
    id: int,
    dados: FomentoUpdate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    fomento = session.get(Fomento, id)
    if not fomento:
        raise HTTPException(404, "Fomento não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(fomento, campo, valor)
    session.add(fomento)
    _commit(session)
    session.refresh(fomento)
    return fomento


@router.delete("/{id}", status_code=204)
def deletar_fomento(
    id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    """Exclusão física ordenada, respeitando todas as chaves estrangeiras."""
    fomento = session.get(Fomento, id)
    if not fomento:
        raise HTTPException(404, "Fomento não encontrado")

    classes = session.exec(
        select(ModalidadeClasse).where(ModalidadeClasse.fomento_id == id)
    ).all()
    subclasses = session.exec(
        select(ModalidadeSubclasse).where(ModalidadeSubclasse.fomento_id == id)
    ).all()
    classe_ids = [classe.id for classe in classes]
    subclasse_ids = [sub.id for sub in subclasses]

    if classe_ids:
        caracteristicas = session.exec(
            select(CaracteristicaModalidade).where(
                CaracteristicaModalidade.classe_id.in_(classe_ids)
            )
        ).all()
        for caract in caracteristicas:
            session.delete(caract)

    if subclasse_ids:
        caracteristicas_sub = session.exec(
            select(CaracteristicaModalidade).where(
                CaracteristicaModalidade.subclasse_id.in_(subclasse_ids)
            )
        ).all()
        ids_existentes = {c.id for c in session.deleted}
        for caract in caracteristicas_sub:
            if caract.id not in ids_existentes:
                session.delete(caract)

    for sub in subclasses:
        session.delete(sub)
    for classe in classes:
        session.delete(classe)
    session.delete(fomento)

    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Não foi possível remover o fomento porque ainda existem registros "
                "relacionados. Verifique submissões ou outras tabelas dependentes."
            ),
        ) from exc


@router.get("/{id}/hierarquia", response_model=HierarquiaFomentoRead)
def hierarquia_fomento(
    id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user),
):
    fomento = session.get(Fomento, id)
    if not fomento:
        raise HTTPException(404, "Fomento não encontrado")

    classes = session.exec(
        select(ModalidadeClasse).where(
            ModalidadeClasse.fomento_id == id,
            ModalidadeClasse.ativo == True,
        )
    ).all()

    resultado = []
    for classe in classes:
        subclasses = session.exec(
            select(ModalidadeSubclasse).where(
                ModalidadeSubclasse.fomento_id == id,
                ModalidadeSubclasse.escopo == classe.escopo,
                ModalidadeSubclasse.ativo == True,
            )
        ).all()
        itens = []
        for sub in subclasses:
            caract = session.exec(
                select(CaracteristicaModalidade).where(
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
    _: Usuario = Depends(get_current_user),
):
    return session.exec(
        select(ModalidadeClasse).where(
            ModalidadeClasse.fomento_id == fomento_id,
            ModalidadeClasse.ativo == True,
        )
    ).all()


@router.post("/{fomento_id}/classes", response_model=ModalidadeClasseRead, status_code=201)
def criar_classe(
    fomento_id: int,
    dados: ModalidadeClasseCreate,
    session: Session = Depends(get_session),
    _: Usuario = Depends(requer_superusuario),
):
    fomento = session.get(Fomento, fomento_id)
    if not fomento or not fomento.ativo:
        raise HTTPException(404, "Fomento não encontrado")
    if dados.escopo not in ("8k", "16k"):
        raise HTTPException(422, "escopo deve ser '8k' ou '16k'")
    classe = ModalidadeClasse(**dados.model_dump())
    session.add(classe)
    _commit(session)
    session.refresh(classe)
    return classe


@router.get("/{fomento_id}/subclasses", response_model=List[ModalidadeSubclasseRead])
def listar_subclasses(
    fomento_id: int,
    escopo: str = "8k",
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user),
):
    return session.exec(
        select(ModalidadeSubclasse).where(
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
    _: Usuario = Depends(requer_superusuario),
):
    fomento = session.get(Fomento, fomento_id)
    if not fomento or not fomento.ativo:
        raise HTTPException(404, "Fomento não encontrado")
    if dados.escopo not in ("8k", "16k"):
        raise HTTPException(422, "escopo deve ser '8k' ou '16k'")
    subclasse = ModalidadeSubclasse(**dados.model_dump())
    session.add(subclasse)
    _commit(session)
    session.refresh(subclasse)
    return subclasse
