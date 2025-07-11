import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from madr.app import app
from madr.database import get_session
from madr.models import Conta, Livro, Romancista, table_registry
from madr.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def conta(session):
    password = 'secret'

    conta = Conta(
        username='Test',
        email='test@test.com',
        password=get_password_hash(password),
    )

    session.add(conta)
    session.commit()
    session.refresh(conta)

    conta.clean_password = password  # type: ignore

    return conta


@pytest.fixture
def token(client, conta):
    response = client.post(
        '/auth/token',
        data={'username': conta.email, 'password': conta.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def romancista(session):
    romancista = Romancista(nome='Hermann Hesse')

    session.add(romancista)
    session.commit()
    session.refresh(romancista)

    return romancista


@pytest.fixture
def livro(session):
    livro = Livro(ano=1927, titulo='o lobo da estepe', romancista_id=1)

    session.add(livro)
    session.commit()
    session.refresh(livro)

    return livro
