import json
import traceback
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.models.base import get_session
from app.models.fomento import (
    Fomento,
    ModalidadeClasse,
    ModalidadeSubclasse,
    CaracteristicaModalidade,
)
from app.models.produtor import Produtor
from app.models.submissao import Submissao
from app.schemas.formulario import FormularioDadosRead, CaracteristicaFormulario
from app.core.security import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/formulario", tags=["Formulário"])


@router.get(
    "/{produtor_id}/{fomento_id}",
    response_model=FormularioDadosRead,
)
def get_dados_formulario(
    produtor_id: int,
    fomento_id: int,
    classe_id: Optional[int] = None,
    subclasse_id: Optional[int] = None,
    session: Session = Depends(get_session),
    _: Usuario = Depends(get_current_user),
):
    try:
        produtor = session.get(Produtor, produtor_id)
        if not produtor or not produtor.ativo:
            raise HTTPException(status_code=404, detail="Produtor não encontrado.")

        fomento = session.get(Fomento, fomento_id)
        if not fomento or not fomento.ativo:
            raise HTTPException(status_code=404, detail="Fomento não encontrado.")

        classe = session.get(ModalidadeClasse, classe_id) if classe_id else None
        subclasse = session.get(ModalidadeSubclasse, subclasse_id) if subclasse_id else None

        caracteristica_raw = None
        if classe_id and subclasse_id:
            caracteristica_raw = session.exec(
                select(CaracteristicaModalidade)
                .where(CaracteristicaModalidade.classe_id == classe_id)
                .where(CaracteristicaModalidade.subclasse_id == subclasse_id)
            ).first()

        caracteristica = None
        if caracteristica_raw:
            def parse_json(valor):
                if isinstance(valor, str):
                    try:
                        return json.loads(valor)
                    except Exception:
                        return []
                return valor or []

            memoria = parse_json(caracteristica_raw.memoria_calculo)
            mao_obra = parse_json(caracteristica_raw.mao_obra_especializada)

            itens_memoria = [
                {
                    "discriminacao": str(i.get("discriminacao", "")),
                    "quantidade": float(i.get("quantidade", 0) or 0),
                    "valor_unitario": float(i.get("valor_unitario", 0) or 0),
                    "subtotal": float(i.get("subtotal", 0) or 0),
                }
                for i in memoria if isinstance(i, dict)
            ]

            itens_mao_obra = [
                {
                    "descricao": str(i.get("descricao", "")),
                    "visitas": float(i.get("visitas", i.get("qtd", 0)) or 0),
                    "valor_unitario": float(i.get("valor_unitario", 0) or 0),
                    "subtotal": float(i.get("subtotal", 0) or 0),
                }
                for i in mao_obra if isinstance(i, dict)
            ]

            caracteristica = CaracteristicaFormulario(
                id=caracteristica_raw.id,
                justificativa=caracteristica_raw.justificativa or "",
                entidade_elaboracao=getattr(caracteristica_raw, "entidade_elaboracao", "") or "",
                texto_entidade_responsavel=getattr(caracteristica_raw, "texto_entidade_responsavel", "") or "",
                itens_investimento=itens_memoria,
                itens_mao_obra=itens_mao_obra,
            )

        submissao = session.exec(
            select(Submissao)
            .where(Submissao.produtor_id == produtor_id)
            .where(Submissao.fomento_id == fomento_id)
            .order_by(Submissao.id.desc())
        ).first()

        return FormularioDadosRead(
            produtor=produtor,
            fomento=fomento,
            classe=classe,
            subclasse=subclasse,
            caracteristica=caracteristica,
            submissao_id=submissao.id if submissao else None,
            numero_processo=submissao.numero_processo if submissao else None,
            municipio_data=submissao.municipio_data if submissao else None,
            data_assinatura=submissao.data_assinatura if submissao else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno ao montar formulário: {str(e)}")
