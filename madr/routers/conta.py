from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr.database import get_session
from madr.helpers import sanitize_str
from madr.models import Conta
from madr.schemas import ContaList, ContaPublic, ContaSchema, Message
from madr.security import get_current_conta, get_password_hash, verify_password

router = APIRouter(prefix='/conta', tags=['conta'])

Session = Annotated[Session, Depends(get_session)]
CurrentConta = Annotated[Conta, Depends(get_current_conta)]


@router.get('/', status_code=HTTPStatus.OK, response_model=ContaList)
def retorna_contas(session: Session):
    contas = session.scalars(select(Conta))

    return {'contas': contas}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=ContaPublic)
def cria_conta(conta: ContaSchema, session: Session):
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

    db_conta = session.scalar(
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
    session.commit()
    session.refresh(db_conta)

    return db_conta


@router.put(
    '/{conta_id}',
    status_code=HTTPStatus.OK,
    response_model=ContaPublic,
)
def alteracao_conta(
    conta_id: int,
    conta: ContaSchema,
    session: Session,
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

    session.commit()
    session.refresh(current_conta)

    return current_conta


@router.delete(
    '/{conta_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_conta(
    conta_id: int,
    session: Session,
    current_conta: CurrentConta,
):
    if current_conta.id != conta_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Sem permissões suficientes.',
        )

    session.delete(current_conta)
    session.commit()

    return {'message': 'Conta deletada com sucesso.'}
