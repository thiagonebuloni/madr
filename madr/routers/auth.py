from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr.database import get_session
from madr.models import Conta
from madr.schemas import Token
from madr.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])

FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[Session, Depends(get_session)]


@router.post('/token', response_model=Token)
def login_for_access_token(
    form_data: FormData,
    session: Session,
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
