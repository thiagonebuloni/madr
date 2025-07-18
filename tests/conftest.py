import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from madr.app import app
from madr.database import get_session
from madr.models import Conta, Livro, Romancista, table_registry
from madr.security import get_password_hash


@pytest_asyncio.fixture
async def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def conta(session):
    password = 'secret'

    conta = Conta(
        username='Test',
        email='test@test.com',
        password=get_password_hash(password),
    )

    session.add(conta)
    await session.commit()
    await session.refresh(conta)

    conta.clean_password = password  # type: ignore

    return conta


@pytest_asyncio.fixture
async def token(client, conta):
    response = client.post(
        '/auth/token',
        data={'username': conta.email, 'password': conta.clean_password},
    )

    return response.json()['access_token']


@pytest_asyncio.fixture
async def romancista(session):
    romancista = Romancista(nome='hermann hesse')

    session.add(romancista)
    await session.commit()
    await session.refresh(romancista)

    return romancista


@pytest_asyncio.fixture
async def livro(session, romancista):
    livro = Livro(
        ano=1927, titulo='o lobo da estepe', romancista_id=romancista.id
    )

    session.add(livro)
    await session.commit()
    await session.refresh(livro)

    return livro
