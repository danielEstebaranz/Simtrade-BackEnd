# Documentacion del BackEnd

Esta carpeta recoge la documentacion funcional del backend actual de Simtrade-BackEnd. Incluye las clases Python del proyecto y los scripts principales que coordinan la autenticacion, el mercado y la persistencia en Firestore.

## Archivos documentados

- [ApiHandler.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/ApiHandler.md): acceso a Finnhub y transformacion de cotizaciones.
- [api_server.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/api_server.md): API HTTP sencilla para login y registro desde el frontend.
- [DbHandler.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/DbHandler.md): conexion con Firestore, autenticacion simple y operaciones de usuario.
- [glosario_tecnico.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/glosario_tecnico.md): explicacion de terminos tecnicos del backend y por que se usan.
- [main.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/main.md): flujo principal de consola para registro, login, logout y operativa del usuario.
- [worker_precios.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/worker_precios.md): sincronizacion periodica de precios desde Finnhub hacia Firestore.

## Cobertura actual

Tras revisar el codigo Python del repositorio, las clases propias actualmente son:

- `ApiHandler`
- `DbHandler`

Ademas, el backend tiene dos scripts principales sin clases propias:

- `api_server.py`
- `main.py`
- `services/worker_precios.py`

## Dependencias del backend

Segun [requirements.txt](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/requirements.txt:1), el backend usa:

- `python-dotenv`
- `finnhub-python`
- `firebase-admin`

## Variables de entorno necesarias

- `FINNHUB_API_KEY`
- `FIREBASE_JSON_PATH`

## Colecciones de Firestore usadas

- `usuarios`: usuarios registrados, saldo, cartera y password en formato hash.
- `mercado`: precio actual y variacion de cada activo sincronizado.
- `transacciones`: historial de compras y ventas por usuario.

## Resumen de arquitectura

- `ApiHandler` consulta Finnhub y devuelve datos en un formato sencillo para el proyecto.
- `DbHandler` encapsula Firestore y centraliza registro, login, cartera, saldo e historial.
- `api_server.py` expone endpoints HTTP muy simples para que el frontend pueda registrar e iniciar sesion sin duplicar logica.
- `worker_precios.py` actualiza la coleccion `mercado` cada 60 segundos.
- `main.py` gestiona el acceso del usuario y la operativa contra Firestore usando los precios ya sincronizados.

## Decisiones de diseno

- Se ha separado el acceso a Finnhub en `ApiHandler` para no mezclar llamadas externas con logica de base de datos o interfaz.
- Se ha concentrado Firestore en `DbHandler` para tener un unico punto de acceso a usuarios, mercado e historial.
- Se ha mantenido `main.py` como aplicacion de consola porque es una forma facil de probar el flujo sin depender del frontend.
- Se ha creado `api_server.py` con FastAPI para tener una API REST sencilla, legible y mas comoda de consumir desde el frontend.
- Se ha dejado `worker_precios.py` como proceso separado porque actualizar precios continuamente no deberia bloquear ni el login ni la aplicacion de usuario.
