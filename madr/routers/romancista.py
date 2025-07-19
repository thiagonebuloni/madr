from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database import get_session
from madr.helpers import sanitize_str
from madr.models import Conta, Romancista
from madr.schemas import (
    Message,
    RomancistaList,
    RomancistaPublic,
    RomancistaSchema,
)
from madr.security import get_current_conta

router = APIRouter(prefix='/romancista', tags=['romancista'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentConta = Annotated[Conta, Depends(get_current_conta)]


@router.get(
    '/{romancista_id}',
    status_code=HTTPStatus.OK,
    response_model=RomancistaPublic,
)
async def retorna_romancista(romancista_id: int, session: Session):  # type: ignore
    db_romancista = await session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não encontrada no MADR.',
        )

    return db_romancista


@router.get('/', status_code=HTTPStatus.OK, response_model=RomancistaList)
async def retorna_romancista_por_nome(
    session: Session,  # type: ignore
    romancista_nome: str | None = None,
    limit: int | None = 10,
    offset: int = 0,
):
    if romancista_nome is None:
        query = await session.scalars(
            select(Romancista).limit(limit).offset(offset)
        )
    else:
        query = await session.scalars(
            select(Romancista)
            .where(Romancista.nome.like(f'%{romancista_nome}%'))
            .limit(limit)
            .offset(offset)
        )

    romancistas = query.all()

    return {'romancistas': romancistas}


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=RomancistaPublic
)
async def cria_romancista(
    romancista: RomancistaSchema,
    session: Session,  # type: ignore
    current_conta: CurrentConta,
):
    db_romancista = await session.scalar(
        select(Romancista).where(Romancista.nome == romancista.nome)
    )

    if db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Romancista já existe.'
        )

    nome_romancista_sanitized = sanitize_str(romancista.nome)
    db_romancista = Romancista(nome=nome_romancista_sanitized)

    session.add(db_romancista)
    await session.commit()
    await session.refresh(db_romancista)

    return db_romancista


@router.delete(
    '/{romancista_id}', status_code=HTTPStatus.OK, response_model=Message
)
async def deleta_romancista(
    romancista_id: int,
    session: Session,  # type: ignore
    current_conta: CurrentConta,
):
    db_romancista = await session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não encontrada no MADR.',
        )

    await session.delete(db_romancista)
    await session.commit()

    return {'message': 'Romancista deletada do MADR.'}


@router.patch(
    '/{romancista_id}',
    status_code=HTTPStatus.OK,
    response_model=RomancistaPublic,
)
async def atualiza_romancista(
    romancista_id: int,
    romancista: RomancistaSchema,
    session: Session,  # type: ignore
    current_conta: CurrentConta,
):
    db_romancista = await session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não encontrada no MADR.',
        )

    db_romancista.nome = sanitize_str(romancista.nome)

    session.add(db_romancista)
    await session.commit()
    await session.refresh(db_romancista)

    return db_romancista
