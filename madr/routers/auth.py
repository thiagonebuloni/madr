from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database import get_session
from madr.models import Conta
from madr.schemas import Token
from madr.security import (
    create_access_token,
    get_current_conta,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentConta = Annotated[Conta, Depends(get_current_conta)]


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: FormData,
    session: Session,
):
    conta = await session.scalar(
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


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(conta: CurrentConta):
    new_access_token = create_access_token(data={'sub': conta.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}
