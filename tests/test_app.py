from http import HTTPStatus

from fastapi.testclient import TestClient

from madr.app import app


def test_app_retorna_ola_mundo():
    client = TestClient(app)
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}
