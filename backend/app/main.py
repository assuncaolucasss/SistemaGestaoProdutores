import traceback
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


@router.get("/", response_model=List[SubmissaoRead])
def listar_submissoes(
    produtor_id: Optional[int] = None,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user)
):
    try:
        query = select(Submissao)
        if produtor_id:
            query = query.where(Submissao.produtor_id == produtor_id)
        return session.exec(query).all()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao listar submissões: {str(e)}")
