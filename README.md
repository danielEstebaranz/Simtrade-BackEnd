# SimTrade - Simulador de Inversiones

Este repositorio contiene el backend del proyecto SimTrade, un TFG orientado a simular operaciones de inversion de forma didactica y segura.

## Componentes principales

- [main.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/main.py:1): aplicacion de consola para registro, login, cartera, compras, ventas e historial.
- [api_server.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/api_server.py:1): API HTTP sencilla para login y registro desde el frontend.
- [services/worker_precios.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/worker_precios.py:1): sincronizador de precios desde Finnhub hacia Firestore.
- [services/Api_Handler.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/Api_Handler.py:1): acceso a Finnhub.
- [services/db_handler.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/db_handler.py:1): acceso a Firestore y logica de usuarios.

## Dependencias

Instaladas desde [requirements.txt](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/requirements.txt:1):

- `python-dotenv`
- `finnhub-python`
- `firebase-admin`

## Variables de entorno

- `FINNHUB_API_KEY`
- `FIREBASE_JSON_PATH`
- `SIMTRADE_API_HOST`
- `SIMTRADE_API_PORT`

## Documentacion

La documentacion detallada del backend esta en [docs/backend/README.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/README.md:1).
