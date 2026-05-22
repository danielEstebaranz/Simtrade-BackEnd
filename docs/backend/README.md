# Documentacion del BackEnd

Esta carpeta recoge la documentacion funcional del backend actual de Simtrade-BackEnd. Incluye las clases Python del proyecto, los scripts principales y la migracion hacia Firebase Authentication.

## Archivos documentados

- [ApiHandler.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/ApiHandler.md): acceso a Finnhub y transformacion de cotizaciones.
- [api_server.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/api_server.md): API REST final con Firebase Authentication, configuracion, fondos, bonos, cartera y mercado.
- [DbHandler.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/DbHandler.md): conexion con Firestore, perfiles, bonos, cartera, saldo e historial.
- [errores_migracion.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/errores_migracion.md): incidencias reales encontradas durante la migracion y como se resolvieron.
- [firebase_auth_migracion.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/firebase_auth_migracion.md): resumen del cambio definitivo a Firebase Authentication.
- [ganancias_cartera.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/ganancias_cartera.md): calculo de ganancias totales, ganancias diarias y valor actual por posicion de la cartera.
- [glosario_tecnico.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/glosario_tecnico.md): explicacion de terminos tecnicos del backend y por que se usan.
- [main.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/main.md): flujo principal de consola para registro, login, logout y operativa del usuario.
- [worker_precios.md](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/worker_precios.md): sincronizacion periodica de precios desde Finnhub hacia Firestore y reinversion automatica de dividendos simulados.

## Cobertura actual

Las clases propias principales del backend son:

- `ApiHandler`
- `DbHandler`

Y los scripts principales son:

- `api_server.py`
- `main.py`
- `services/worker_precios.py`

## Dependencias del backend

Segun [requirements.txt](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/requirements.txt:1), el backend usa:

- `python-dotenv`
- `finnhub-python`
- `firebase-admin`
- `fastapi`
- `uvicorn`
- `yfinance`
- `requests`

## Variables de entorno necesarias

- `FINNHUB_API_KEY`
- `FIREBASE_JSON_PATH`
- `FIREBASE_WEB_API_KEY`
- `SIMTRADE_API_HOST`
- `SIMTRADE_API_PORT`

## Resumen de arquitectura

- `ApiHandler` consulta Finnhub y devuelve datos en un formato sencillo para el proyecto.
- `DbHandler` encapsula Firestore y centraliza perfiles, configuracion, bonos, cartera, saldo e historial.
- `api_server.py` expone endpoints HTTP para autenticacion, configuracion, fondos, bonos, borrado de cuenta, cartera, compra desde mercado, venta desde cartera, tendencias y ganancias.
- El frontend consume la configuracion desde `/panel/configuracion` para modo claro/oscuro, anadir fondos, quitar fondos, reiniciar cartera y borrar cuenta.
- El frontend consume `/panel/bonos` para mostrar ofertas de bonos, crear inversiones a 60 segundos, refrescar contadores, liquidar vencidos y reflejar el rastro en historial.
- El asistente IA de soporte se integra fuera de este backend mediante n8n; la API Python no participa en ese flujo.
- `worker_precios.py` actualiza la coleccion `mercado` cada 60 segundos y aplica dividendos simulados reinvertidos en la misma accion.
- `main.py` mantiene una app de consola para pruebas y operativa local usando tambien Firebase Authentication.

## Decisiones de diseno

- Se ha separado el acceso a Finnhub en `ApiHandler` para no mezclar llamadas externas con logica de base de datos o interfaz.
- Se ha concentrado Firestore en `DbHandler` para tener un unico punto de acceso a usuarios, configuracion, bonos, saldo, mercado e historial.
- Se ha creado `api_server.py` con FastAPI para tener una API REST sencilla, legible y mas comoda de consumir desde el frontend.
- La autenticacion queda delegada en Firebase Authentication, mientras Firestore guarda solo el perfil y los datos de negocio.
- Los bonos viven en una coleccion separada porque tienen estado (`active` o `settled`), vencimiento (`maturity_at`) y liquidacion (`settled_at`).
- La consola y la API usan el mismo criterio de autenticacion para evitar dobles sistemas y errores de compatibilidad entre web y terminal.
- Se ha dejado `worker_precios.py` como proceso separado porque actualizar precios y aplicar reinversiones periodicas no deberia bloquear ni el login ni la aplicacion de usuario.
