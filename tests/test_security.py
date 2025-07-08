from jwt import decode

from madr.security import (
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=['HS256'])

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_password():
    hashed = get_password_hash('test')
    assert verify_password('test', hashed)
