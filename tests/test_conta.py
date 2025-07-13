from http import HTTPStatus

from madr.schemas import ContaPublic


def test_cria_conta_sucesso(client):
    response = client.post(
        '/conta/',
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


def test_cria_conta_usuario_ja_existe(client, conta):
    response = client.post(
        '/conta/',
        json={
            'username': 'Test',
            'email': 'test@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Conta já existe.'}


def test_cria_conta_email_ja_existe(client, conta):
    response = client.post(
        '/conta/',
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
        '/conta/',
        json={
            'email': 'teste@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_cria_conta_email_none(client):
    response = client.post(
        '/conta/',
        json={
            'username': 'Test',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_cria_conta_password_none(client):
    response = client.post(
        '/conta/',
        json={
            'username': 'Test',
            'email': 'test@test.com',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_retorna_contas(client, conta):
    response = client.get('/conta/')

    assert response


def test_retorna_conta_with_conta(client, conta):
    conta_schema = ContaPublic.model_validate(conta).model_dump()
    response = client.get('/conta/')
    assert response.json() == {'contas': [conta_schema]}


def test_username_is_sanitized(client):
    response = client.post(
        '/conta/',
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


def test_alterando_conta_sucesso(client, conta, token):
    response = client.put(
        f'/conta/{conta.id}',
        headers={'Authorization': f'Bearer {token}'},
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


def test_alterando_conta_username_none(client, conta, token):
    conta.username = ''
    response = client.put(
        f'/conta/{conta.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'email': 'nebu@email.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Dados não podem ser nulos.'}


def test_alterando_conta_email_none(client, conta, token):
    conta.email = ''
    response = client.put(
        f'/conta/{conta.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'nebu',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Não foi possível validar as credenciais.'
    }


def test_alterando_conta_password_none(client, conta, token):
    conta.password = ''
    response = client.put(
        f'/conta/{conta.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'nebu',
            'email': 'nebu@email.com',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Dados não podem ser nulos.'}


def test_alterando_conta_conta_not_found(client, conta, token):
    response = client.put(
        '/conta/10',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'nebu',
            'email': 'nebu@email.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissões suficientes.'}


def test_alterando_conta_conta_dados_iguais(client, conta, token):
    response = client.put(
        f'/conta/{conta.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Test',
            'email': 'test@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_alteracao_conta_decode_error(client, token):
    token += 'b'
    response = client.put(
        '/conta/{conta.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Test',
            'email': 'test@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Não foi possível validar as credenciais.'
    }


def test_deleta_conta(client, conta, token):
    response = client.delete(
        f'/conta/{conta.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Conta deletada com sucesso.'}


def test_deleta_conta_errada(client, conta, token):
    response = client.delete(
        '/conta/10',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Sem permissões suficientes.'}


def test_deleta_conta_nao_encontrada(client):
    response = client.delete('/conta/1')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}
