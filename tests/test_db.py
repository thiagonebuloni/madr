from dataclasses import asdict

from sqlalchemy import select

from madr.models import Conta


def test_create_conta(session):
    nova_conta = Conta(
        username='nebu', email='nebu@mail.com', password='secret'
    )
    session.add(nova_conta)
    session.commit()

    conta = session.scalar(select(Conta).where(Conta.username == 'nebu'))

    assert asdict(conta) == {
        'id': 1,
        'username': 'nebu',
        'email': 'nebu@mail.com',
        'password': 'secret',
    }


def test_session(session):
    nova_conta = Conta(
        username='nebu', email='nebu@mail.com', password='secret'
    )
    session.add(nova_conta)
    session.commit()

    assert session
