import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from services.db_handler import DbHandler
from services.Api_Handler import ApiHandler

load_dotenv()

HOST = os.getenv('SIMTRADE_API_HOST', '127.0.0.1')
PORT = int(os.getenv('SIMTRADE_API_PORT', '8000'))
ALLOWED_ORIGINS = [
    'http://127.0.0.1:4200',
    'http://localhost:4200',
]

app = FastAPI(title='Simtrade API',version='1.0.0',)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=['POST', 'GET'],
    allow_headers=['*'],
)

db = DbHandler(os.getenv('FIREBASE_JSON_PATH'))
market_api = ApiHandler(os.getenv('FINNHUB_API_KEY'))


class AuthRequest(BaseModel):
    username: str
    password: str


def normalize_user_id(username):
    return username.strip().lower()


def public_user(user_id):
    user_data = db.obtener_usuario(user_id)
    return {
        'id': user_id,
        'username': user_data.get('username', user_id),
        'saldo': user_data.get('saldo', 1000.0),
        'cartera': user_data.get('cartera', {}),
    }


@app.get('/')
def healthcheck():
    return {'message': 'Simtrade API activa.'}


@app.get('/users/{username}/portfolio')
def get_user_portfolio(username: str):
    user_id = normalize_user_id(username)
    posiciones = db.obtener_cartera(user_id)

    return {
        'user': public_user(user_id),
        'portfolio': posiciones,
        'total_activos': len(posiciones),
    }


@app.get('/market/{ticker}/trend')
def get_market_trend(ticker: str, rango: str = Query('1d', alias='range')):
    if rango not in {'1d', '1w', '1y'}:
        raise HTTPException(
            status_code=400,
            detail='El rango debe ser 1d, 1w o 1y.',
        )

    tendencia = market_api.obtener_tendencia(ticker, rango)

    if tendencia is None or not tendencia.get('points'):
        raise HTTPException(
            status_code=404,
            detail='No hay datos de tendencia para ese activo.',
        )

    return tendencia


@app.post('/auth/login')
def login(payload: AuthRequest):
    username = payload.username.strip()
    password = payload.password.strip()

    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail='Usuario y contrasena son obligatorios.',
        )

    ok, result = db.autenticar_usuario(username, password)
    if not ok:
        raise HTTPException(status_code=401, detail=result)

    return {
        'message': 'Inicio de sesion correcto.',
        'user': public_user(result),
    }


@app.post('/auth/register', status_code=201)
def register(payload: AuthRequest):
    username = payload.username.strip()
    password = payload.password.strip()

    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail='Usuario y contrasena son obligatorios.',
        )

    ok, result = db.crear_usuario(username, password)
    if not ok:
        raise HTTPException(status_code=409, detail=result)

    return {
        'message': 'Usuario creado correctamente.',
        'user': public_user(result),
    }


if __name__ == '__main__':
    uvicorn.run('api_server:app', host=HOST, port=PORT, reload=False)
