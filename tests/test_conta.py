from http import HTTPStatus

from madr.schemas import ContaPublic


def test_cria_conta_sucesso(client):
    response = client.post(
        '/contas/',
        json={
            'username': 'nebu',
            'email': 'nebu@email.com',
            'password': 'secrets',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'nebu',
        'email': 'nebu@email.com',
    }


def test_cria_conta_usuario_ja_existe(conta, client):
    response = client.post(
        '/contas/',
        json={
            'username': 'Test',
            'email': 'test@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Conta já existe.'}


def test_cria_conta_email_ja_existe(conta, client):
    response = client.post(
        '/contas/',
        json={
            'username': 'Teste',
            'email': 'test@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Conta já existe.'}


def test_cria_conta_usuario_none(client):
    response = client.post(
        '/contas/',
        json={
            'email': 'teste@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_cria_conta_email_none(client):
    response = client.post(
        '/contas/',
        json={
            'username': 'Test',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_cria_conta_password_none(client):
    response = client.post(
        '/contas/',
        json={
            'username': 'Test',
            'email': 'test@test.com',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_read_contas(client, conta):
    response = client.get('/contas/')

    assert response


def test_read_conta_with_conta(client, conta):
    conta_schema = ContaPublic.model_validate(conta).model_dump()
    response = client.get('/contas/')
    assert response.json() == {'contas': [conta_schema]}


def test_username_is_sanitized(client):
    response = client.post(
        '/contas/',
        json={
            'username': 'NEBU2',
            'email': 'nebu2@email.com',
            'password': 'secret',
        },
    )

    assert response.json() == {
        'id': 1,
        'username': 'nebu2',
        'email': 'nebu2@email.com',
    }


def test_alterando_conta_sucesso(client, conta):
    response = client.put(
        '/contas/1',
        json={
            'username': 'nebu',
            'email': 'nebu@email.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'nebu',
        'email': 'nebu@email.com',
    }


def test_alterando_conta_username_none(client):
    response = client.put(
        '/contas/1',
        json={
            'email': 'nebu@email.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_alterando_conta_email_none(client):
    response = client.put(
        '/contas/1',
        json={
            'username': 'nebu',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_alterando_conta_password_none(client):
    response = client.put(
        '/contas/1',
        json={
            'username': 'nebu',
            'email': 'nebu@email.com',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_alterando_conta_conta_not_found(client, conta):
    response = client.put(
        '/contas/10',
        json={
            'username': 'nebu',
            'email': 'nebu@email.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_alterando_conta_conta_dados_iguais(client, conta):
    response = client.put(
        '/contas/1',
        json={
            'username': 'Test',
            'email': 'test@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_deleta_conta(client, conta):
    response = client.delete('/contas/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Conta deletada com sucesso.'}


def test_deleta_conta_nao_encontrada(client):
    response = client.delete('/contas/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Conta não encontrada.'}
