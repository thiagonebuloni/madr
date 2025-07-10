from http import HTTPStatus


def test_cria_livro(client):
    response = client.post(
        '/livro',
        json={'ano': 1927, 'titulo': 'O Lobo da Estepe', 'romancista_id': 1},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'ano': 1927,
        'titulo': 'o lobo da estepe',
        'romancista_id': 1,
    }


def test_cria_livro_conflict(client, livro):
    response = client.post(
        '/livro',
        json={'ano': 1927, 'titulo': 'o lobo da estepe', 'romancista_id': 1},
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


def test_retorna_livros(client, livro):
    response = client.get('/livro/')

    assert response.status_code == HTTPStatus.OK


def test_retorna_livros_por_nome(client, livro):
    titulo_pesquisa = livro.titulo.split()[3]
    response = client.get(f'livro/?livro_nome={titulo_pesquisa}')

    assert response.status_code == HTTPStatus.OK


def test_retorna_livros_por_nome_ano(client, livro):
    titulo_pesquisa = livro.titulo.split()[3]
    response = client.get(
        f'livro/?livro_nome={titulo_pesquisa}&livro_ano=1927'
    )

    assert response.status_code == HTTPStatus.OK


def test_deleta_livro(client, livro):
    response = client.delete('/livro/1')

    assert response.status_code == HTTPStatus.OK


def test_deleta_livro_not_found(client):
    response = client.delete('/livro/1')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_atualiza_livro(client, livro):
    response = client.patch(
        '/livro/1',
        json={
            'ano': 1927,
            'titulo': 'loobo da estepe',
            'romancista_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.OK


def test_atualiza_livro_not_found(client):
    response = client.patch(
        '/livro/1',
        json={
            'ano': 1927,
            'titulo': 'loobo da estepe',
            'romancista_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
