from dataclasses import asdict

import pytest
from sqlalchemy import select

from madr.models import Conta


@pytest.mark.asyncio
async def test_create_conta(session):
    nova_conta = Conta(
        username='nebu', email='nebu@mail.com', password='secret'
    )
    session.add(nova_conta)
    await session.commit()

    conta = await session.scalar(select(Conta).where(Conta.username == 'nebu'))

    assert asdict(conta) == {
        'id': 1,
        'username': 'nebu',
        'email': 'nebu@mail.com',
        'password': 'secret',
    }
