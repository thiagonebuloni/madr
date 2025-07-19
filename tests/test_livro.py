from http import HTTPStatus


def test_cria_livro(client, token, romancista):
    response = client.post(
        '/livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1927,
            'titulo': 'O Lobo da Estepe',
            'romancista_id': romancista.id,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'ano': 1927,
        'titulo': 'o lobo da estepe',
        'romancista_id': 1,
    }


def test_cria_livro_romancista_not_found(client, token):
    response = client.post(
        '/livro',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1927,
            'titulo': 'O Lobo da Estepe',
            'romancista_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista não consta no MADR.'}


def test_cria_livro_conflict(client, livro, romancista, token):
    response = client.post(
        '/livro/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': livro.ano,
            'titulo': livro.titulo,
            'romancista_id': romancista.id,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_retorna_livro(client, livro):
    response = client.get('/livro/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'ano': 1927,
        'titulo': 'o lobo da estepe',
        'romancista_id': 1,
    }


def test_retorna_livro_not_found(client):
    response = client.get('/livro/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro não consta no MADR.'}


def test_retorna_livro_por_nome_ano_sem_dados(client, livro):
    response = client.get('/livro/')

    assert response.status_code == HTTPStatus.OK


def test_retorna_livros_por_nome(client, livro):
    titulo_pesquisa = livro.titulo.split()[3]
    response = client.get(f'livro/?livro_nome={titulo_pesquisa}')

    assert response.status_code == HTTPStatus.OK


def test_retorna_livros_por_ano(client, livro):
    response = client.get(f'livro/?livro_ano={livro.ano}')

    assert response.status_code == HTTPStatus.OK


def test_deleta_livro(client, livro, token):
    response = client.delete(
        '/livro/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK


def test_deleta_livro_not_found(client, token, romancista):
    response = client.delete(
        '/livro/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_atualiza_livro(client, livro, token):
    response = client.patch(
        '/livro/1',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1927,
            'titulo': 'loobo da estepe',
            'romancista_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.OK


def test_atualiza_livro_not_found(client, token, romancista):
    response = client.patch(
        '/livro/1',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1927,
            'titulo': 'loobo da estepe',
            'romancista_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
