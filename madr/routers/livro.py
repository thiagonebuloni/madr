from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from madr.database import get_session
from madr.helpers import sanitize_str
from madr.models import Conta, Livro
from madr.schemas import (
    LivroList,
    LivroPublic,
    LivroSchema,
    Message,
)
from madr.security import get_current_conta

router = APIRouter(prefix='/livro', tags=['livro'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=LivroPublic)
def cria_livro(
    livro: LivroSchema,
    session: Session = Depends(get_session),
    current_conta: Conta = Depends(get_current_conta),
):
    livro.titulo = sanitize_str(livro.titulo)

    db_livro = session.scalar(
        select(Livro).where(Livro.titulo == livro.titulo)
    )

    if db_livro:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Livro já existente.'
        )

    db_livro = Livro(
        ano=livro.ano, titulo=livro.titulo, romancista_id=livro.romancista_id
    )

    session.add(db_livro)
    session.commit()
    session.refresh(db_livro)

    return db_livro


@router.get(
    '/{livro_id}', status_code=HTTPStatus.OK, response_model=LivroPublic
)
def retorna_livro(livro_id: int, session: Session = Depends(get_session)):
    livro = session.scalar(select(Livro).where(Livro.id == livro_id))

    if not livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro não consta no MADR.',
        )

    return livro


@router.get('/', status_code=HTTPStatus.OK, response_model=LivroList)
def retorna_livro_por_nome_ano(
    livro_nome: str | None = None,
    livro_ano: int | None = None,
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    if livro_nome and livro_ano:
        livros = session.scalars(
            select(Livro)
            .where(
                Livro.titulo.like(f'%{livro_nome}%'), Livro.ano == livro_ano
            )
            .offset(offset)
            .limit(limit)
        )
    else:
        livros = session.scalars(
            select(Livro)
            .where(
                or_(
                    Livro.titulo.like(f'%{livro_nome}%'),
                    Livro.ano == livro_ano,
                )
            )
            .offset(offset)
            .limit(limit)
        )

    return {'livros': livros}


@router.delete(
    '/{livro_id}', status_code=HTTPStatus.OK, response_model=Message
)
def deleta_livro(
    livro_id: int,
    session: Session = Depends(get_session),
    current_conta: Conta = Depends(get_current_conta),

):
    livro = session.scalar(select(Livro).where(Livro.id == livro_id))
    if not livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro não consta no MADR.',
        )

    session.delete(livro)
    session.commit()

    return {'message': 'Livro deletado do MADR.'}


@router.patch(
    '/{livro_id}', status_code=HTTPStatus.OK, response_model=LivroPublic
)
def atualiza_livro(
    livro_id: int,
    livro: LivroSchema,
    session: Session = Depends(get_session),
    current_conta: Conta = Depends(get_current_conta),
):
    db_livro = session.scalar(select(Livro).where(Livro.id == livro_id))

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
    session.commit()
    session.refresh(db_livro)

    return db_livro
