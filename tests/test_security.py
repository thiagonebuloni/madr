from http import HTTPStatus

import pytest
from jwt import DecodeError, decode

from madr.security import (
    create_access_token,
    get_password_hash,
    settings,
    verify_password,
)


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_token_invalido(client):
    response = client.delete(
        '/conta/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Não foi possível validar as credenciais.'
    }


def test_jwt_decode_error():
    data = {'test': 'test'}
    token = create_access_token(data)
    token += 'b'

    with pytest.raises(DecodeError):
        decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_password():
    hashed = get_password_hash('test')
    assert verify_password('test', hashed)
