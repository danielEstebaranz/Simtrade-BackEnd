import os

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import auth as firebase_auth
from pydantic import BaseModel
import requests
import uvicorn

from services.Api_Handler import ApiHandler
from services.db_handler import DbHandler

load_dotenv()

HOST = os.getenv('SIMTRADE_API_HOST', '127.0.0.1')
PORT = int(os.getenv('SIMTRADE_API_PORT', '8000'))
FIREBASE_WEB_API_KEY = os.getenv('FIREBASE_WEB_API_KEY', '').strip()
ALLOWED_ORIGINS = [
    'http://127.0.0.1:4200',
    'http://localhost:4200',
]

app = FastAPI(
    title='Simtrade API',
    version='2.0.0',
    description='API REST preparada para Firebase Authentication.',
)

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
    username: str | None = None
    email: str | None = None
    password: str


class RegisterRequest(BaseModel):
    email: str | None = None
    username: str
    password: str


def resolve_email(email, username):
    email_value = (email or '').strip().lower()
    username_value = username.strip()

    if email_value:
        return email_value

    if '@' in username_value:
        return username_value.lower()

    return ''


def resolve_display_name(username, email):
    username_value = username.strip()

    if username_value and '@' not in username_value:
        return username_value

    if email:
        return email.split('@', 1)[0]

    return username_value


def extract_bearer_token(authorization):
    if not authorization:
        raise HTTPException(status_code=401, detail='Falta cabecera Authorization.')

    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Authorization debe usar Bearer token.')

    return authorization.split(' ', 1)[1].strip()


def verify_current_user(authorization):
    id_token = extract_bearer_token(authorization)

    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token['uid']
    except Exception:
        raise HTTPException(status_code=401, detail='Token no valido o expirado.')


def public_user(user_id):
    return db.obtener_perfil_publico(user_id)


def firebase_sign_in(email, password):
    if not FIREBASE_WEB_API_KEY:
        raise HTTPException(
            status_code=500,
            detail='Falta configurar FIREBASE_WEB_API_KEY en el entorno.',
        )

    response = requests.post(
        f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}',
        json={
            'email': email,
            'password': password,
            'returnSecureToken': True,
        },
        timeout=30,
    )

    if response.status_code == 200:
        return response.json()

    try:
        error_code = response.json().get('error', {}).get('message', '')
    except ValueError:
        error_code = ''

    errores = {
        'EMAIL_NOT_FOUND': 'No existe una cuenta con ese email.',
        'INVALID_PASSWORD': 'La contrasena no es correcta.',
        'USER_DISABLED': 'La cuenta esta deshabilitada.',
        'INVALID_LOGIN_CREDENTIALS': 'Las credenciales no son correctas.',
    }
    raise HTTPException(
        status_code=401,
        detail=errores.get(error_code, 'No se pudo iniciar sesion con Firebase Authentication.'),
    )


@app.get('/')
def healthcheck():
    return {'message': 'Simtrade API activa.'}


@app.get('/auth/me')
def get_current_user_profile(authorization: str | None = Header(default=None)):
    user_id = verify_current_user(authorization)
    return {
        'message': 'Usuario autenticado.',
        'user': public_user(user_id),
    }


@app.get('/users/me/portfolio')
def get_my_portfolio(authorization: str | None = Header(default=None)):
    user_id = verify_current_user(authorization)
    posiciones = db.obtener_cartera(user_id)

    return {
        'user': public_user(user_id),
        'portfolio': posiciones,
        'total_activos': len(posiciones),
    }


@app.get('/market/{ticker}/trend')
def get_market_trend(ticker: str, range: str = Query('1d')):
    if range not in {'1d', '1w', '1y'}:
        raise HTTPException(status_code=400, detail='El rango debe ser 1d, 1w o 1y.')

    tendencia = market_api.obtener_tendencia(ticker, range)
    if tendencia is None or not tendencia.get('points'):
        raise HTTPException(status_code=404, detail='No hay datos de tendencia para ese activo.')

    return tendencia


@app.post('/auth/login')
def login_help(payload: AuthRequest):
    identificador = (payload.email or payload.username or '').strip()
    password = payload.password.strip()

    if not identificador or not password:
        raise HTTPException(status_code=400, detail='Usuario/email y contrasena son obligatorios.')

    email = resolve_email(payload.email, identificador)
    if not email:
        raise HTTPException(status_code=400, detail='Debes usar un email valido para iniciar sesion.')

    firebase_session = firebase_sign_in(email, password)
    user_id = firebase_session.get('localId')

    return {
        'message': 'Inicio de sesion correcto.',
        'user': public_user(user_id),
        'idToken': firebase_session.get('idToken'),
        'refreshToken': firebase_session.get('refreshToken'),
    }


@app.post('/auth/register', status_code=201)
def register(payload: RegisterRequest):
    username = payload.username.strip()
    email = resolve_email(payload.email, username)
    display_name = resolve_display_name(username, email)
    password = payload.password.strip()

    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail='Usuario y contrasena son obligatorios.',
        )

    if not email:
        raise HTTPException(
            status_code=400,
            detail='Debes indicar un email valido para registrar el usuario.',
        )

    try:
        user_record = firebase_auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=409,
            detail=f'No se pudo crear el usuario en Firebase Auth: {exc}',
        )

    db.crear_perfil_auth(user_record.uid, email, display_name)

    return {
        'message': 'Usuario creado correctamente en Firebase Authentication.',
        'user': public_user(user_record.uid),
    }


if __name__ == '__main__':
    uvicorn.run('api_server:app', host=HOST, port=PORT, reload=False)
