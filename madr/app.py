from http import HTTPStatus

from fastapi import FastAPI

from madr.routers import auth, conta
from madr.schemas import Message

app = FastAPI()

app.include_router(conta.router)
app.include_router(auth.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá mundo!'}
