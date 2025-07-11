from http import HTTPStatus

import pytest
from jwt import DecodeError, decode

from madr.security import (
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=['HS256'])

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
        decode(token, SECRET_KEY, algorithms=['HS256'])


def test_password():
    hashed = get_password_hash('test')
    assert verify_password('test', hashed)
