# Errores, puntos debiles y FAQ

## Errores corregidos

### El frontend no podia usar el backend de consola

#### Causa

El backend funcionaba con `input()` y `print()`. Eso sirve para consola, pero un navegador no puede llamar directamente a funciones Python.

#### Solucion

Se creo `api_server.py` con FastAPI.

Ahora Angular llama por HTTP:

```text
POST /auth/login
POST /auth/register
GET /users/{username}/portfolio
GET /market/{ticker}/trend
```

### CORS bloqueaba llamadas del navegador

#### Causa

Frontend y backend corren en puertos distintos:

```text
Frontend: http://localhost:4200
Backend:  http://127.0.0.1:8000
```

El navegador exige permiso para esa comunicacion.

#### Solucion

Se anadio `CORSMiddleware` en FastAPI y se permitieron:

```text
http://127.0.0.1:4200
http://localhost:4200
```

### La grafica del frontend no era real

#### Causa

El frontend tenia un fallback que fabricaba datos cuando fallaba la API.

#### Solucion

Se quito el fallback del frontend y se creo el endpoint real:

```text
GET /market/{ticker}/trend?range=1d
```

El historico sale de `yfinance`.

### `finnhub` rompia el import

#### Causa

`Api_Handler.py` importaba `finnhub` siempre. Si la libreria no estaba instalada, fallaba todo el archivo aunque solo se quisiera usar yfinance.

#### Solucion

Se convirtio en import opcional:

```py
try:
    import finnhub
except ImportError:
    finnhub = None
```

### El endpoint devolvia datos antiguos

#### Causa

Habia un proceso viejo escuchando en el puerto `8000`.

#### Solucion

Se paro el proceso antiguo y se arranco el backend actualizado.

## Librerias usadas y motivo

### FastAPI

Framework HTTP del backend. Se usa porque es sencillo, claro y valida entradas con Pydantic.

### Uvicorn

Servidor que ejecuta FastAPI.

### firebase-admin

SDK oficial para hablar con Firestore desde Python.

### python-dotenv

Carga `.env` para no hardcodear rutas o claves dentro del codigo.

### finnhub-python

Se mantiene para precio actual y worker de mercado.

### yfinance

Se usa para obtener historicos reales de mercado. Es la libreria que alimenta la grafica de cartera.

## Metodologia seguida

### Separar consola y API

`main.py` sigue existiendo como aplicacion de consola.

`api_server.py` es la capa que entiende HTTP.

Asi no se rompe la consola mientras se anade frontend.

### No duplicar Firestore

La API reutiliza `DbHandler`. No se ha creado una segunda forma de autenticar usuarios ni una segunda estructura de datos.

### Un servicio por responsabilidad

- `DbHandler`: base de datos
- `ApiHandler`: datos de mercado
- `api_server.py`: rutas HTTP
- `main.py`: interfaz de consola

### Fallar de forma visible

Para graficas, si no hay datos reales se devuelve error. No se inventan datos en backend ni en frontend.

## Puntos debiles actuales

### Seguridad de autenticacion

No hay JWT, cookies seguras ni expiracion de sesion.

Para produccion se deberia implementar autenticacion real.

### Hash de contrasena

Se usa SHA-256 simple. Es mejor que texto plano, pero no es lo ideal.

Mejora recomendada:

```text
bcrypt
argon2
```

### Variables sensibles

`service_account.json` y `.env` no deberian subirse a un repositorio publico.

### No hay validacion profunda de tickers

El backend acepta el ticker en la URL y lo pasa al proveedor. Si el ticker no existe, devuelve `404`.

### No hay cache

Cada peticion de tendencia pide datos externos. Podria optimizarse con cache temporal.

### No hay tests automatizados

Se ha validado con build y llamadas manuales, pero no hay suite de tests.

## Preguntas tipicas

### Por que no se llama a Firestore desde Angular

Porque Firestore contiene datos sensibles y reglas de negocio. Es mejor que Angular llame al backend.

### Por que `api_server.py` no sustituye a `main.py`

Porque tienen objetivos distintos:

- `main.py`: probar y usar por consola.
- `api_server.py`: servir al frontend por HTTP.

### Por que hay Finnhub y yfinance

Finnhub ya estaba en el proyecto para precio actual y worker.

yfinance se anadio para historicos reales de graficas, porque es mas simple para este caso.

### Que pasa si no tengo `FINNHUB_API_KEY`

La parte de precio actual con Finnhub no funcionara. La grafica historica puede seguir funcionando con yfinance.

### Que pasa si yfinance no devuelve datos

El endpoint devuelve `404` y el frontend muestra error.

### Como compruebo que la grafica es real

Llama al endpoint:

```powershell
curl.exe -s -i "http://127.0.0.1:8000/market/AAPL/trend?range=1d"
```

Debe aparecer:

```json
"source": "yfinance"
```

### Donde veo documentacion interactiva

Con el backend arrancado:

```text
http://127.0.0.1:8000/docs
```
