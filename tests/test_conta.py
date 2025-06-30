from http import HTTPStatus

from fastapi.testclient import TestClient

from madr.app import app


def test_cria_conta_sucesso():
    client = TestClient(app)

    response = client.post(
        '/contas/',
        json={
            'username': 'nebu',
            'email': 'nebu@email.com',
            'password': 'secrets',
        },
    )

    assert response.status_code == HTTPStatus.CREATED


def test_cria_conta_usuario_ja_existe():
    client = TestClient(app)

    response = client.post(
        '/contas/',
        json={
            'username': 'username',
            'email': 'username@email.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_username_is_sanitized():
    client = TestClient(app)

    response = client.post(
        '/contas/',
        json={
            'username': 'NEBU',
            'email': 'nebu@email.com',
            'password': 'secret',
        },
    )

    assert response.json() == {
        'id': 2,
        'username': 'nebu',
        'email': 'nebu@email.com',
    }
