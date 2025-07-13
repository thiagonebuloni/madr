from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, conta):
    response = client.post(
        '/auth/token',
        data={'username': conta.email, 'password': conta.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_token_not_conta(client):
    response = client.post(
        '/auth/token',
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_get_token_access_token(client, conta):
    response = client.post(
        '/auth/token',
        data={'username': conta.email, 'password': conta.clean_password},
    )

    token = response.json()

    assert token
    assert response.json() == token
    assert token['access_token']
    assert token['token_type'] == 'bearer'


def test_get_token_unauthorized_username(client, conta):
    response = client.post(
        '/auth/token',
        data={'username': 'conta.username', 'password': conta.clean_password},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_token_unauthorized_password(client, conta):
    response = client.post(
        '/auth/token',
        data={'username': conta.email, 'password': conta.password},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_token_expirado_apos_tempo(client, conta):
    with freeze_time('2025-07-13 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': conta.email,
                'password': conta.clean_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-07-13 13:01:00'):
        response = client.put(
            f'/conta/{conta.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongpassword',
                'email': 'usuarioerrado@email.com',
                'password': 'wrong',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'detail': 'Não foi possível validar as credenciais.'
        }


def test_refresh_token(client, conta, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expirado_nao_consegue_refresh(client, conta):
    with freeze_time('2025-07-13 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': conta.email,
                'password': conta.clean_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-07-13 13:01:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'detail': 'Não foi possível validar as credenciais.'
        }
