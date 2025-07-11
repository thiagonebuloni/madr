from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr.database import get_session
from madr.models import Conta, Romancista
from madr.schemas import (
    Message,
    RomancistaList,
    RomancistaPublic,
    RomancistaSchema,
)
from madr.security import get_current_conta

router = APIRouter(prefix='/romancista', tags=['romancista'])


@router.get(
    '/{romancista_id}',
    status_code=HTTPStatus.OK,
    response_model=RomancistaPublic,
)
def retorna_romancista(
    romancista_id: int, session: Session = Depends(get_session)
):
    db_romancista = session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não encontrada no MADR.',
        )

    return db_romancista


@router.get('/', status_code=HTTPStatus.OK, response_model=RomancistaList)
def retorna_romancista_por_nome(
    romancista_nome: str | None = None,
    limit: int | None = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    romancistas = session.scalars(
        select(Romancista)
        .where(Romancista.nome.like(f'%{romancista_nome}%'))
        .limit(limit)
        .offset(offset)
    )

    return {'romancistas': romancistas}


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=RomancistaPublic
)
def cria_romancista(
    romancista: RomancistaSchema,
    session: Session = Depends(get_session),
    current_conta: Conta = Depends(get_current_conta),
):
    db_romancista = session.scalar(
        select(Romancista).where(Romancista.nome == romancista.nome)
    )

    if db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Romancista já existe.'
        )

    db_romancista = Romancista(nome=romancista.nome)

    session.add(db_romancista)
    session.commit()
    session.refresh(db_romancista)

    return db_romancista


@router.delete(
    '/{romancista_id}', status_code=HTTPStatus.OK, response_model=Message
)
def deleta_romancista(
    romancista_id: int,
    session: Session = Depends(get_session),
    current_conta: Conta = Depends(get_current_conta),
):
    db_romancista = session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não encontrada no MADR.',
        )

    session.delete(db_romancista)
    session.commit()

    return {'message': 'Romancista deletada do MADR.'}


@router.patch(
    '/{romancista_id}',
    status_code=HTTPStatus.OK,
    response_model=RomancistaPublic,
)
def atualiza_romancista(
    romancista_id: int,
    romancista: RomancistaSchema,
    session: Session = Depends(get_session),
    current_conta: Conta = Depends(get_current_conta),
):
    db_romancista = session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não encontrada no MADR.',
        )

    db_romancista.nome = romancista.nome

    session.add(db_romancista)
    session.commit()
    session.refresh(db_romancista)

    return db_romancista
