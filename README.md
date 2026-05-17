# SimTrade - Simulador de Inversiones

Este repositorio contiene el backend del proyecto SimTrade, un TFG orientado a simular operaciones de inversion de forma didactica y segura.

## Componentes principales

- [main.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/main.py:1): aplicacion de consola para registro, login, cartera, compras, ventas e historial.
- [api_server.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/api_server.py:1): API HTTP para autenticacion, configuracion, fondos, cartera, historico y mercado desde el frontend.
- [services/worker_precios.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/worker_precios.py:1): sincronizador de precios desde Finnhub hacia Firestore.
- [services/Api_Handler.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/Api_Handler.py:1): acceso a Finnhub para precio actual y yfinance para historicos.
- [services/db_handler.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/db_handler.py:1): acceso a Firestore y logica de usuarios.

## Dependencias

Instaladas desde [requirements.txt](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/requirements.txt:1):

- `python-dotenv`
- `finnhub-python`
- `firebase-admin`
- `fastapi`
- `uvicorn`
- `yfinance`
- `requests`

## Variables de entorno

- `FINNHUB_API_KEY`
- `FIREBASE_JSON_PATH`
- `SIMTRADE_API_HOST`
- `SIMTRADE_API_PORT`

## Documentacion

La documentacion detallada del backend esta en [docs/backend/README.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/README.md:1).

## Nota sobre el asistente IA

El asistente virtual de soporte no forma parte de este backend Python. Vive como integracion externa en n8n y el frontend lo consume directamente mediante HTTP. El backend sigue siendo responsable de autenticacion, datos de negocio y mercado.
