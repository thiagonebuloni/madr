from http import HTTPStatus

from fastapi.testclient import TestClient

from madr.app import app


def test_app_retorna_ola_mundo():
    client = TestClient(app)
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}


def test_get_token(client, conta):
    response = client.post(
        '/auth/token',
        data={'username': conta.email, 'password': conta.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_token_unauthorized_username(client, conta):
    response = client.post(
        '/auth/token',
        data={'username': conta.username, 'password': conta.clean_password},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_token_unauthorized_password(client, conta):
    response = client.post(
        '/auth/token',
        data={'username': conta.email, 'password': conta.password},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
