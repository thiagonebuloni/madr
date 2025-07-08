from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr.database import get_session
from madr.models import Conta
from madr.schemas import ContaList, ContaPublic, ContaSchema, Message, Token
from madr.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá mundo!'}


@app.get('/contas', status_code=HTTPStatus.OK, response_model=ContaList)
def retorna_contas(session: Session = Depends(get_session)):
    contas = session.scalars(select(Conta))

    return {'contas': contas}


@app.post(
    '/contas', status_code=HTTPStatus.CREATED, response_model=ContaPublic
)
def cria_conta(conta: ContaSchema, session: Session = Depends(get_session)):
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

    username_sanitized = conta.username.lstrip().rstrip().strip().lower()

    db_conta = Conta(
        username=username_sanitized,
        email=conta.email,
        password=get_password_hash(conta.password),
    )

    session.add(db_conta)
    session.commit()
    session.refresh(db_conta)

    return db_conta


@app.put(
    '/contas/{conta_id}',
    status_code=HTTPStatus.OK,
    response_model=ContaPublic,
)
def alteracao_conta(
    conta_id: int, conta: ContaSchema, session: Session = Depends(get_session)
):
    if conta.username is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Dados não podem ser nulos.',
        )

    if conta.email is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Dados não podem ser nulos.',
        )

    if conta.password is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Dados não podem ser nulos.',
        )

    db_conta = session.scalar(select(Conta).where(Conta.id == conta_id))

    if not db_conta:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado'
        )

    if (
        db_conta.username == conta.username
        and db_conta.email == conta.email
        and verify_password(conta.password, db_conta.password)
    ):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Os novos dados não podem ser iguais aos existentes.',
        )

    db_conta.username = conta.username
    db_conta.email = conta.email
    db_conta.password = get_password_hash(conta.password)

    session.commit()
    session.refresh(db_conta)

    return db_conta


@app.delete('/contas/{id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_conta(id: int, session: Session = Depends(get_session)):
    db_conta = session.scalar(select(Conta).where(Conta.id == id))

    if not db_conta:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Conta não encontrada.'
        )

    session.delete(db_conta)
    session.commit()

    return {'message': 'Conta deletada com sucesso.'}


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    conta = session.scalar(
        select(Conta).where(Conta.email == form_data.username)
    )

    if not conta:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Email ou password incorreto.',
        )

    if not verify_password(form_data.password, conta.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Email ou password incorreto.',
        )

    access_token = create_access_token(data={'sub': conta.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
