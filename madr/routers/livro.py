from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database import get_session
from madr.helpers import sanitize_str
from madr.models import Conta, Livro, Romancista
from madr.schemas import (
    LivroFilter,
    LivroList,
    LivroPublic,
    LivroSchema,
    Message,
)
from madr.security import get_current_conta

router = APIRouter(prefix='/livro', tags=['livro'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentConta = Annotated[Conta, Depends(get_current_conta)]
FilterLivros = Annotated[LivroFilter, Query()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=LivroPublic)
async def cria_livro(
    livro: LivroSchema,
    session: Session,  # type: ignore
    current_conta: CurrentConta,
):
    livro.titulo = sanitize_str(livro.titulo)

    db_livro = await session.scalar(
        select(Livro).where(Livro.titulo == livro.titulo)
    )

    if db_livro:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Livro já existente.'
        )

    romancista = await session.scalar(
        select(Romancista).where(Romancista.id == livro.romancista_id)
    )

    if not romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não consta no MADR.',
        )

    db_livro = Livro(
        ano=livro.ano, titulo=livro.titulo, romancista_id=livro.romancista_id
    )

    session.add(db_livro)
    await session.commit()
    await session.refresh(db_livro)

    return db_livro


@router.get(
    '/{livro_id}', status_code=HTTPStatus.OK, response_model=LivroPublic
)
async def retorna_livro(livro_id: int, session: Session):  # type: ignore
    livro = await session.scalar(select(Livro).where(Livro.id == livro_id))

    if not livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro não consta no MADR.',
        )

    return livro


@router.get('/', status_code=HTTPStatus.OK, response_model=LivroList)
async def retorna_livro_por_nome_ano(
    session: Session,  # type: ignore
    livro_filter: FilterLivros,
):
    if livro_filter.titulo and livro_filter.ano:
        query = await session.scalars(
            select(Livro)
            .where(
                Livro.titulo.like(f'%{livro_filter.titulo}%'),
                Livro.ano == livro_filter.ano,
            )
            .offset(livro_filter.offset)
            .limit(livro_filter.limit)
        )
    elif livro_filter.titulo or livro_filter.ano:
        query = await session.scalars(
            select(Livro)
            .where(
                or_(
                    Livro.titulo.like(f'%{livro_filter.titulo}%'),
                    Livro.ano == livro_filter.ano,
                )
            )
            .offset(livro_filter.offset)
            .limit(livro_filter.limit)
        )
    else:
        query = await session.scalars(
            select(Livro).offset(livro_filter.offset).limit(livro_filter.limit)
        )

    livros = query.all()

    return {'livros': livros}


@router.delete(
    '/{livro_id}', status_code=HTTPStatus.OK, response_model=Message
)
async def deleta_livro(
    livro_id: int,
    session: Session,  # type: ignore
    current_conta: CurrentConta,
):
    livro = await session.scalar(select(Livro).where(Livro.id == livro_id))
    if not livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro não consta no MADR.',
        )

    await session.delete(livro)
    await session.commit()

    return {'message': 'Livro deletado do MADR.'}


@router.patch(
    '/{livro_id}', status_code=HTTPStatus.OK, response_model=LivroPublic
)
async def atualiza_livro(
    livro_id: int,
    livro: LivroSchema,
    session: Session,  # type: ignore
    current_conta: CurrentConta,
):
    db_livro = await session.scalar(select(Livro).where(Livro.id == livro_id))

    if not db_livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro não consta no MADR.',
        )

    titulo_sanitized = sanitize_str(livro.titulo)

    db_livro.ano = livro.ano
    db_livro.titulo = titulo_sanitized
    db_livro.romancista_id = livro.romancista_id

    session.add(db_livro)
    await session.commit()
    await session.refresh(db_livro)

    return db_livro
