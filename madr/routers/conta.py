from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database import get_session
from madr.helpers import sanitize_str
from madr.models import Conta
from madr.schemas import (
    ContaList,
    ContaPublic,
    ContaSchema,
    FilterPage,
    Message,
)
from madr.security import get_current_conta, get_password_hash, verify_password

router = APIRouter(prefix='/conta', tags=['conta'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentConta = Annotated[Conta, Depends(get_current_conta)]
FilterContas = Annotated[FilterPage, Query()]


@router.get('/', status_code=HTTPStatus.OK, response_model=ContaList)
async def retorna_contas(
    session: Session,  # type: ignore
    filter_contas: FilterContas,
):
    query = await session.scalars(
        select(Conta).offset(filter_contas.offset).limit(filter_contas.limit)
    )
    contas = query.all()

    return {'contas': contas}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=ContaPublic)
async def cria_conta(conta: ContaSchema, session: Session):  # type: ignore
    if conta.username is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Nome de usuário não pode ser nulo',
        )

    if conta.email is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Email não pode ser nulo',
        )

    if conta.password is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Password não pode ser nulo',
        )

    db_conta = await session.scalar(
        select(Conta).where(
            (Conta.username == conta.username) | (Conta.email == conta.email)
        )
    )

    if db_conta:
        if db_conta.username == conta.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Conta já existe.',
            )
        elif db_conta.email == conta.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Conta já existe.'
            )

    username_sanitized = sanitize_str(conta.username)

    db_conta = Conta(
        username=username_sanitized,
        email=conta.email,
        password=get_password_hash(conta.password),
    )

    session.add(db_conta)
    await session.commit()
    await session.refresh(db_conta)

    return db_conta


@router.put(
    '/{conta_id}',
    status_code=HTTPStatus.OK,
    response_model=ContaPublic,
)
async def alteracao_conta(
    conta_id: int,
    conta: ContaSchema,
    session: Session,  # type: ignore
    current_conta: CurrentConta,
):
    if current_conta.id != conta_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Sem permissões suficientes.',
        )

    if conta.username is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Dados não podem ser nulos.',
        )

    if conta.password is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Dados não podem ser nulos.',
        )

    if (
        current_conta.username == conta.username
        and current_conta.email == conta.email
        and verify_password(conta.password, current_conta.password)
    ):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Os novos dados não podem ser iguais aos existentes.',
        )

    current_conta.username = conta.username
    current_conta.email = conta.email  # type: ignore
    current_conta.password = get_password_hash(conta.password)

    await session.commit()
    await session.refresh(current_conta)

    return current_conta


@router.delete(
    '/{conta_id}', status_code=HTTPStatus.OK, response_model=Message
)
async def delete_conta(
    conta_id: int,
    session: Session,  # type: ignore
    current_conta: CurrentConta,
):
    if current_conta.id != conta_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Sem permissões suficientes.',
        )

    await session.delete(current_conta)
    await session.commit()

    return {'message': 'Conta deletada com sucesso.'}
