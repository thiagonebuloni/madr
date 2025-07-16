from http import HTTPStatus


def test_cria_romancista(client, token):
    response = client.post(
        '/romancista/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'nome': 'Roberto Bolaños',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'id': 1, 'nome': 'Roberto Bolaños'}


def test_cria_romancista_conflict(client, romancista, token):
    response = client.post(
        '/romancista',
        json={'nome': 'Hermann Hesse'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_retorna_romancista(client, romancista):
    response = client.get('/romancista/1')

    assert response.status_code == HTTPStatus.OK


def test_retorna_romancista_not_found(client):
    response = client.get('/romancista/1')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_retorna_romancista_por_nome(client, romancista):
    response = client.get('/romancista/?romancista_nome=e')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'romancistas': [{'id': 1, 'nome': 'Hermann Hesse'}]
    }


def test_retorna_romancista_sem_nome(client, romancista):
    response = client.get('/romancista/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'romancistas': [{'id': 1, 'nome': 'Hermann Hesse'}]
    }


def test_deleta_romancista(client, romancista, token):
    response = client.delete(
        '/romancista/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Romancista deletada do MADR.'}


def test_deleta_romancista_not_found(client, token):
    response = client.delete(
        '/romancista/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista não encontrada no MADR.'}


def test_atualiza_romancista(client, romancista, token):
    response = client.patch(
        '/romancista/1',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Hermann Hessee'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'nome': 'Hermann Hessee'}


def test_atualiza_romancista_not_found(client, token):
    response = client.patch(
        '/romancista/1',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Hermann Hessee'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista não encontrada no MADR.'}
