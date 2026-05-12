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

### El puerto 8000 ya estaba ocupado

#### Causa

Al intentar arrancar `api_server.py`, Windows devolvio:

```text
[WinError 10048] solo se permite un uso de cada direccion de socket
```

Ya habia un proceso escuchando en `127.0.0.1:8000`.

#### Solucion

Se localizo el proceso:

```powershell
netstat -ano | Select-String ":8000"
```

Y se paro:

```powershell
Stop-Process -Id <PID> -Force
```

### Faltaba `FIREBASE_WEB_API_KEY`

#### Causa

El login contra Firebase Authentication necesita la Web API Key del proyecto Firebase.

El `.env` tenia `FINNHUB_API_KEY` y `FIREBASE_JSON_PATH`, pero faltaba:

```env
FIREBASE_WEB_API_KEY=...
```

#### Solucion

Se debe anadir en el `.env` del backend y reiniciar el servidor.

La clave se obtiene en Firebase Console:

```text
Configuracion del proyecto -> General -> App web -> apiKey
```

### Firestore se conectaba dos veces

#### Causa

El backend arrancaba Uvicorn con:

```py
uvicorn.run('api_server:app', ...)
```

Al ejecutar el archivo directamente, eso podia reimportar el modulo y crear dos inicializaciones visibles.

#### Solucion

Se cambio a:

```py
uvicorn.run(app, host=HOST, port=PORT, reload=False)
```

### `Ganancias totales` salia como `Sin coste`

#### Causa

El backend no encontraba historial de transacciones para calcular el dinero invertido real.

Ademas, ordenar por `fecha` directamente en Firestore podia requerir indice.

#### Solucion

Se cambio a:

- consultar transacciones por usuario
- ordenar en Python
- calcular coste abierto por historial
- si no hay historial valido, estimar con `1000 - saldo actual`

### Ganancia total positiva y ganancia diaria negativa parecia raro

#### Explicacion

No es un error. La ganancia total compara contra el precio de compra o coste invertido. La diaria compara contra el primer precio del dia.

Ejemplo:

```text
Ganancia total:  +0,02 $
Ganancia diaria: -0,06 $
```

Puede pasar si la posicion sigue por encima de tu compra, pero hoy ha bajado.

### Compra desde mercado devolvia `Not Found`

#### Causa

El frontend llamaba a:

```text
POST /users/me/portfolio/buy
```

pero el backend que estaba arrancado en el puerto `8000` era una version antigua que todavia no tenia ese endpoint.

#### Solucion

Se reinicio el backend para cargar `api_server.py` actualizado.

### La compra pedia acciones y no dinero

#### Causa

La primera version del popup enviaba `quantity`, es decir, numero de unidades.

#### Solucion

Se cambio el contrato a:

```json
{
  "ticker": "AAPL",
  "amount": 10
}
```

Ahora el usuario introduce dinero a invertir y el backend calcula:

```text
quantity = amount / price
```

### El campo del popup sobresalia

#### Causa

El input tenia `width: 100%`, pero su padding y borde se sumaban al ancho total.

#### Solucion

Se anadio `box-sizing: border-box` al popup y sus hijos.

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

### Ganancias estimadas

Si no hay historial de compras, el backend estima el dinero invertido con:

```text
1000 - saldo actual
```

Esto es valido para el proyecto actual, pero no es tan exacto como guardar coste medio real por activo.

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

### Como compruebo las ganancias

Hace falta un `idToken` obtenido en login:

```powershell
curl.exe -s -i "http://127.0.0.1:8000/users/me/portfolio/gains" -H "Authorization: Bearer <idToken>"
```

Sin token debe devolver `401`.

### Como compruebo la compra

Hace falta un `idToken` obtenido en login:

```powershell
curl.exe -s -i "http://127.0.0.1:8000/users/me/portfolio/buy" -H "Authorization: Bearer <idToken>" -H "Content-Type: application/json" -d "{\"ticker\":\"AAPL\",\"amount\":10}"
```

Si el usuario tiene saldo suficiente, debe devolver usuario actualizado y datos de la operacion.

### Donde veo documentacion interactiva

Con el backend arrancado:

```text
http://127.0.0.1:8000/docs
```
