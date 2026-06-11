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

Se debe añadir en el `.env` del backend y reiniciar el servidor.

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

### Venta desde cartera: el importe no coincidia exactamente

#### Causa

El frontend mostraba un valor de posicion calculado con el ultimo precio de la tendencia cargada. Al vender, el backend consulta de nuevo el precio real para ejecutar la operacion.

Si el precio cambia entre esos dos momentos, vender el 25 % de una posicion que parecia valer 100 $ puede devolver, por ejemplo, 24,66 $.

#### Solucion

Se documento el comportamiento y se cambio la UI para mostrar `Valor actual` en lugar de `Dinero invertido`.

La venta se mantiene usando precio real del backend en el momento de operar.

### El sidebar no llegaba hasta abajo

#### Causa

El frontend tenia el sidebar con `min-height: 100dvh`, que cubre la ventana visible inicial, pero no todo el documento si el contenido crece verticalmente.

#### Solucion

En frontend se corrigio con:

```css
:host {
  position: sticky;
  top: 0;
}

.sidebar {
  height: 100dvh;
}
```

Despues se ajusto el fondo del dashboard para que el lateral se mantenga oscuro hasta abajo:

```css
.app-shell {
  background: #111827;
}

.main-content {
  background: #f8fafc;
}
```

### La primera solucion del sidebar creo un corte visual

#### Causa

Se intento usar un `linear-gradient` con un ancho fijo para pintar la franja del sidebar. Esa medida no coincidio siempre con el ancho real.

#### Solucion

Se elimino el gradiente fijo y se dejo que el layout pinte fondos por capas: contenedor oscuro y contenido principal claro.

### Usuario recien registrado no podia comprar

#### Causa

`POST /auth/register` creaba el usuario en Firebase Authentication y el perfil en Firestore, pero solo devolvia `user`.

El frontend entraba al panel porque tenia usuario, pero no tenia `idToken`. Despues, al comprar, el frontend no podia enviar:

```text
Authorization: Bearer <idToken>
```

Por eso la compra mostraba que el usuario no habia iniciado sesion.

#### Solucion

Despues de crear el usuario, el backend llama tambien a `firebase_sign_in(email, password)` y devuelve:

```json
{
  "user": {},
  "idToken": "...",
  "refreshToken": "..."
}
```

Asi el registro y el login dejan la misma sesion preparada para comprar, vender y consultar cartera.

### El frontend de configuracion necesitaba endpoints reales

#### Causa

La pantalla `/panel/configuracion` del frontend ya existia, pero para que funcionara necesitaba contratos HTTP claros para:

- leer y cambiar tema
- añadir fondos
- retirar fondos
- reiniciar cartera
- borrar cuenta

#### Solucion

El backend expone:

```text
GET /users/me/settings
PATCH /users/me/settings
POST /users/me/funds
POST /users/me/funds/withdraw
POST /users/me/portfolio/reset
POST /users/me/delete
```

Todos usan `Authorization: Bearer <idToken>` y devuelven JSON pensado para que Angular actualice `AuthService`. Las operaciones destructivas piden tambien la contraseña actual.

### Depositos confundidos con compras en el historial

#### Causa

Al añadir fondos, `DbHandler` registra `DEPOSITO`. Si el frontend no lo distingue, puede tratarlo como una compra generica.

#### Solucion

El backend mantiene `type: "deposito"` en la respuesta de historial y el frontend lo muestra como ingreso de saldo.

Esto conserva trazabilidad del saldo y evita mezclar depositos con operaciones de mercado.

### El importe manual de añadir fondos no se aplicaba

#### Causa

Los botones rapidos enviaban una cantidad numerica valida, pero el input manual podia llegar como texto o con un nombre de campo distinto segun el formulario.

#### Solucion

`AddFundsRequest` acepta:

```text
amount
cantidad
value
```

Y `normalize_funds_amount(...)` convierte el valor a `float` antes de validar `math.isfinite`.

### El login cambiaba al modo oscuro

#### Causa

El tema global se aplica en `:root[data-theme='dark']`. Si una pantalla no fija su propia paleta, puede heredar variables oscuras.

#### Solucion

El frontend deja la pantalla de login en `color-scheme: light` y fondo claro fijo para que no cambie aunque el usuario tenga modo oscuro en el panel.

### Los bonos no se liquidaban al llegar a 0

#### Causa

El frontend restaba segundos localmente. Podia mostrar `0` antes de que el backend considerase que `maturity_at` habia llegado. Entonces llamaba a liquidar demasiado pronto, no se liquidaba nada, y no volvia a intentarlo hasta que el usuario entraba otra vez en Bonos.

#### Solucion

- El backend calcula `secondsRemaining` con redondeo hacia arriba.
- El frontend usa `maturityAt` como fuente real del contador.
- Si detecta un bono activo vencido, llama a `POST /users/me/bonds/settle`.
- `GET /users/me/bonds` tambien liquida vencidos al cargar o refrescar la pantalla.

### Los bonos no aparecian en historial

#### Causa

El backend registraba transacciones tecnicas `BONO_INVERSION` y `BONO_CIERRE`, pero el frontend no tenia mensajes especificos para esos tipos.

#### Solucion

El frontend ahora muestra:

```text
Has invertido 1000 $ en un bono de AMZN.
Ha finalizado tu bono de AMZN y has recibido 1020 $.
```

### La estetica de bonos activos quedaba desalineada

#### Causa

Se probo una cascada visual con desplazamiento lateral progresivo, pero al tener varios bonos hacia que la columna pareciera asimetrica.

#### Solucion

La lista de bonos activos se dejo como columna simetrica: todos alineados a la izquierda y con el mismo ancho.

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

### requests

Se usa para llamar al endpoint oficial de Firebase Authentication `signInWithPassword` desde el backend. Esa llamada necesita `FIREBASE_WEB_API_KEY`.

## Librerias usadas en frontend y motivo

### Angular

Framework principal del frontend. Se usa para rutas, componentes standalone, formularios reactivos y renderizado declarativo.

### RxJS

Se usa para manejar respuestas HTTP y suscripciones, junto con `takeUntilDestroyed` para limpiar suscripciones al destruir componentes.

### Chart.js

Se usa en las graficas de mercado y cartera.

### Angular Router

Controla rutas como `/login`, `/panel/cartera`, `/panel/mercado`, `/panel/bonos`, `/panel/historial`, `/panel/configuracion` y `/panel/ayuda`.

### Angular HttpClient

Se usa en servicios como `AuthService`, `MarketService`, `AccountService` y `ChatService` para consumir FastAPI y n8n.

## Metodologia seguida

### Separar consola y API

`main.py` sigue existiendo como aplicacion de consola.

`api_server.py` es la capa que entiende HTTP.

Asi no se rompe la consola mientras se añade frontend.

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

La autenticacion se delega en Firebase Authentication. El backend recibe `idToken` en rutas protegidas y lo verifica antes de acceder a datos privados.

Para produccion convendria reforzar rate limiting, monitorizacion de intentos fallidos y politicas avanzadas de sesion.

### Hash de contraseña

El backend ya no guarda ni compara contraseñas en Firestore, ni en texto plano ni con hash local.

La contraseña se valida contra Firebase Authentication. Los metodos antiguos de hash local se retiraron de `DbHandler`.

Mejora recomendada para produccion:

```text
rate limiting
politicas de contrasena mas estrictas
alertas por intentos repetidos
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

### Diferencia entre valor mostrado y venta ejecutada

El precio de mercado se consulta en distintas peticiones. Una pantalla puede mostrar un valor y la venta puede ejecutarse unos segundos despues con otro precio.

Esto es correcto para datos reales, pero a futuro se podria mostrar una confirmacion con el precio exacto justo antes de vender.

### Borrado irreversible de cuenta

`POST /users/me/delete` y `DELETE /users/me` borran el usuario de Firebase Authentication, el perfil de Firestore, las transacciones y los bonos. En frontend se pide escribir `BORRAR` y despues introducir la contraseña actual. A nivel de backend se exige `idToken` valido y password correcta.

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

### Como compruebo la venta

Hace falta un `idToken` obtenido en login:

```powershell
curl.exe -s -i "http://127.0.0.1:8000/users/me/portfolio/sell" -H "Authorization: Bearer <idToken>" -H "Content-Type: application/json" -d "{\"ticker\":\"AAPL\",\"percentage\":25}"
```

Si el usuario tiene unidades de ese activo, debe devolver usuario actualizado y datos de la venta.

### Como compruebo la configuracion

Hace falta un `idToken` obtenido en login:

```powershell
curl.exe -s -i "http://127.0.0.1:8000/users/me/settings" -H "Authorization: Bearer <idToken>"
```

Para cambiar tema:

```powershell
curl.exe -s -i -X PATCH "http://127.0.0.1:8000/users/me/settings" -H "Authorization: Bearer <idToken>" -H "Content-Type: application/json" -d "{\"theme\":\"dark\"}"
```

### Como compruebo añadir fondos

```powershell
curl.exe -s -i -X POST "http://127.0.0.1:8000/users/me/funds" -H "Authorization: Bearer <idToken>" -H "Content-Type: application/json" -d "{\"amount\":250}"
```

Debe devolver `operation.amount`, `operation.balance` y `user` actualizado.

### Como compruebo borrar cuenta

Usar solo con cuentas de prueba:

```powershell
curl.exe -s -i -X POST "http://127.0.0.1:8000/users/me/delete" -H "Authorization: Bearer <idToken>" -H "Content-Type: application/json" -d "{\"password\":\"contrasena_actual\"}"
```

Debe devolver:

```json
{
  "message": "Cuenta borrada correctamente.",
  "deleted_transactions": 0,
  "deleted_bonds": 0
}
```

### Como compruebo bonos

Ofertas disponibles:

```powershell
curl.exe -s -i "http://127.0.0.1:8000/bonds/offers"
```

Crear un bono de Amazon:

```powershell
curl.exe -s -i -X POST "http://127.0.0.1:8000/users/me/bonds" -H "Authorization: Bearer <idToken>" -H "Content-Type: application/json" -d "{\"ticker\":\"AMZN\",\"amount\":1000}"
```

Consultar y liquidar vencidos automaticamente:

```powershell
curl.exe -s -i "http://127.0.0.1:8000/users/me/bonds" -H "Authorization: Bearer <idToken>"
```

Forzar liquidacion de bonos vencidos:

```powershell
curl.exe -s -i -X POST "http://127.0.0.1:8000/users/me/bonds/settle" -H "Authorization: Bearer <idToken>"
```

### Por que el frontend muestra `Valor actual`

Porque antes de vender interesa saber cuanto vale la posicion ahora mismo:

```text
valor actual = unidades * ultimo precio real
```

`investedCost` sigue existiendo para calcular rentabilidad, pero no es el dato mas claro para ejecutar una venta.

### Donde veo documentacion interactiva

Con el backend arrancado:

```text
http://127.0.0.1:8000/docs
```
