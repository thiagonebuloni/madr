from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from madr.schemas import ContaPublic, ContaSchema, Message

app = FastAPI()


fake_db: list[dict] = [
    {
        'id': 1,
        'username': 'username',
        'email': 'username@email.com',
        'password': 'secret',
    }
]


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá mundo!'}


@app.post(
    '/contas', status_code=HTTPStatus.CREATED, response_model=ContaPublic
)
def cria_conta(conta: ContaSchema):
    last_id: int = 0
    for c in fake_db:
        last_id = c.get('id', 0)
        if conta.username == c['username']:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )

    username_sanitized = conta.username.lstrip().rstrip().strip().lower()

    conta_db = {
        'id': last_id + 1,
        'username': username_sanitized,
        'email': conta.email,
        'password': conta.password,
    }

    fake_db.append(conta_db)

    return conta_db


@app.put(
    '/contas/{id}',
    status_code=HTTPStatus.OK,
    response_model=ContaPublic,
)
def alteracao_conta(id: int, conta: ContaSchema):
    for conta_db in fake_db:
        breakpoint()
        if conta_db['id'] == id:
            continue
            # conta_db = conta

    # conflict if data equal

    # for conta_db in fake_db:
    #     if conta_db['id'] == id:
    #         for dado_db, dado in zip(conta_db, conta):
    #             dado_db = dado

    return conta_db


@app.delete('/contas/{id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_conta(id: int):
    for conta in fake_db:
        if conta['id'] == id:
            fake_db.remove(conta)
    breakpoint()

    return {'message': 'Conta deletada com sucesso'}
