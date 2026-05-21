# api_server

Archivo fuente: [api_server.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/api_server.py)

## Proposito

`api_server.py` expone la API REST principal del backend. Gestiona autenticacion contra Firebase Authentication, consulta de perfil, configuracion, fondos, bonos, borrado de cuenta, cartera, compras, ventas, ganancias y tendencia de mercado para el frontend.

## Responsabilidad dentro del sistema

Este archivo recibe las peticiones HTTP del frontend y coordina tres piezas:

- Firebase Authentication para registro e inicio de sesion
- Firestore para perfil, configuracion, bonos, cartera, saldo e historial
- `ApiHandler` para las tendencias historicas del mercado y valoracion de cartera

## Endpoints actuales

### `GET /`

Comprueba si la API esta levantada.

### `POST /auth/register`

Recibe:

```json
{
  "username": "usuario@email.com",
  "password": "clave_segura"
}
```

Opcionalmente tambien puede recibir:

```json
{
  "email": "usuario@email.com",
  "username": "usuario",
  "password": "clave_segura"
}
```

Funcionamiento:

1. Resuelve el email real.
2. Crea el usuario en Firebase Authentication.
3. Crea el perfil de negocio en Firestore.
4. Inicia sesion automaticamente con Firebase Authentication.
5. Devuelve el usuario publico, `idToken` y `refreshToken`.

Se devuelve token tambien en registro para que el frontend quede en el mismo estado que despues de un login normal. Sin ese token, el usuario podia entrar al panel pero no comprar ni vender.

### `POST /auth/login`

Recibe:

```json
{
  "username": "usuario@email.com",
  "password": "clave_segura"
}
```

Tambien admite `email` si en algun momento el frontend lo envia.

Funcionamiento:

1. Convierte el identificador de entrada en email.
2. Llama al endpoint oficial `signInWithPassword` de Firebase Authentication.
3. Si la autenticacion es correcta, devuelve:
   - `user`
   - `idToken`
   - `refreshToken`

### `GET /auth/me`

Devuelve el perfil publico del usuario autenticado a partir de `Authorization: Bearer <token>`.

### `GET /users/me/portfolio`

Devuelve la cartera del usuario autenticado a partir de `Authorization: Bearer <token>`.

### `GET /users/me/history`

Devuelve las ultimas transacciones del usuario autenticado.

Requiere:

```text
Authorization: Bearer <idToken>
```

Respuesta orientativa:

```json
{
  "items": [
    {
      "id": "abc123",
      "type": "compra",
      "ticker": "AAPL",
      "quantity": 0.15,
      "price": 300.15,
      "total": 45.02,
      "date": "2026-05-13T19:30:00+00:00"
    }
  ]
}
```

El frontend lo usa para la pestaña `Historial`, donde se muestran mensajes como:

```text
Has comprado 0,15 acciones de AAPL a 300,15 $ por 45,02 $.
Has vendido 0,03 acciones de AAPL a 301,10 $ por 9,03 $.
Has anadido 250 $ al saldo.
Has invertido 1000 $ en un bono de AMZN.
Ha finalizado tu bono de AMZN y has recibido 1020 $.
```

Los ingresos de fondos se guardan como `DEPOSITO`, las inversiones de bonos como `BONO_INVERSION` y las liquidaciones como `BONO_CIERRE`. En la respuesta salen en minusculas para Angular: `deposito`, `bono_inversion` y `bono_cierre`.

### `GET /users/me/settings`

Devuelve la configuracion del usuario autenticado. Actualmente incluye el tema visual que usara el frontend:

```json
{
  "settings": {
    "theme": "light"
  },
  "user": {}
}
```

`theme` puede ser:

```text
light -> modo claro
dark  -> modo oscuro
```

El frontend usa este endpoint al abrir `/panel/configuracion`. Si el backend devuelve `dark`, Angular aplica el tema global mediante `ThemeService`.

### `PATCH /users/me/settings`

Actualiza la configuracion del usuario autenticado.

Requiere:

```text
Authorization: Bearer <idToken>
```

Recibe:

```json
{
  "theme": "dark"
}
```

Tambien acepta los alias `oscuro` y `claro`, pero guarda siempre `dark` o `light`.

Respuesta orientativa:

```json
{
  "message": "Configuracion actualizada correctamente.",
  "settings": {
    "theme": "dark"
  },
  "user": {}
}
```

El endpoint devuelve tambien `user` actualizado para que el frontend pueda sincronizar `AuthService` y conservar `settings.theme` en la sesion local.

### `POST /users/me/funds`

Anade fondos al saldo disponible del usuario autenticado.

Requiere:

```text
Authorization: Bearer <idToken>
```

Recibe la cantidad elegida por el usuario:

```json
{
  "amount": 250
}
```

Tambien admite `cantidad` o `value` para evitar fallos si el frontend manda el valor manual con otro nombre de campo.

Funcionamiento:

1. Valida token de Firebase.
2. Valida que la cantidad sea mayor que 0.
3. Limita cada ingreso a un maximo de `100000`.
4. Suma el importe al saldo.
5. Registra el movimiento como `DEPOSITO` en el historial.
6. Devuelve usuario actualizado.

Respuesta orientativa:

```json
{
  "message": "Fondos anadidos correctamente.",
  "operation": {
    "amount": 250,
    "balance": 1250
  },
  "user": {}
}
```

### `POST /users/me/funds/withdraw`

Retira fondos del saldo disponible del usuario autenticado.

Recibe:

```json
{
  "amount": 250
}
```

Reglas:

- la cantidad debe ser mayor que 0
- no puede superar el maximo por operacion
- no puede superar el saldo disponible

Si todo es correcto, registra `RETIRADA` en el historial y devuelve el usuario actualizado.

### `GET /bonds/offers`

Devuelve las ofertas de bonos disponibles. No modifica saldo ni requiere token.

Respuesta orientativa:

```json
{
  "items": [
    {
      "ticker": "AMZN",
      "name": "Amazon",
      "return_percent": 2.0,
      "duration_seconds": 60
    }
  ]
}
```

### `GET /users/me/bonds`

Devuelve los bonos del usuario autenticado. Antes de responder liquida automaticamente los bonos activos que ya hayan cumplido su minuto.

`secondsRemaining` se calcula con redondeo hacia arriba para evitar que el frontend muestre `0` antes de que el backend pueda liquidar realmente el bono.

Respuesta orientativa:

```json
{
  "items": [
    {
      "id": "abc123",
      "ticker": "AMZN",
      "name": "Amazon",
      "amount": 1000,
      "returnPercent": 2,
      "profit": 20,
      "payout": 1020,
      "durationSeconds": 60,
      "secondsRemaining": 41,
      "status": "active",
      "startedAt": "2026-05-21T12:00:00+00:00",
      "maturityAt": "2026-05-21T12:01:00+00:00",
      "settledAt": null
    }
  ],
  "active": [],
  "settled": [],
  "user": {}
}
```

### `POST /users/me/bonds`

Invierte saldo disponible en un bono.

Requiere:

```text
Authorization: Bearer <idToken>
```

Recibe:

```json
{
  "ticker": "AMZN",
  "amount": 1000
}
```

Funcionamiento:

1. Valida token de Firebase.
2. Valida que exista una oferta para el ticker.
3. Comprueba que el usuario tenga saldo suficiente.
4. Resta el importe del saldo.
5. Crea el bono activo con vencimiento a 60 segundos.
6. Registra `BONO_INVERSION` en historial.

Para Amazon, la oferta actual es 2% a 60 segundos. Un importe de `1000` genera:

```text
profit = 20
payout = 1020
```

### `POST /users/me/bonds/settle`

Liquida los bonos vencidos del usuario autenticado. El frontend puede llamarlo al cumplirse el minuto o usar `GET /users/me/bonds`, que ya liquida vencidos antes de responder.

Si hay bonos vencidos:

1. Cambia su estado a `settled`.
2. Suma `payout` al saldo.
3. Registra `BONO_CIERRE` en historial.
4. Devuelve usuario actualizado.

### `POST /users/me/portfolio/reset`

Reinicia la cartera del usuario autenticado.

Recibe:

```json
{
  "confirmation": "REINICIAR",
  "password": "contrasena_actual"
}
```

El backend exige token valido, palabra exacta `REINICIAR` y contrasena correcta antes de:

- dejar el saldo en `1000`
- vaciar la cartera
- registrar la operacion `REINICIO`

### `POST /users/me/delete`

Borra la cuenta verificando antes la contrasena actual. Se usa desde el frontend porque permite enviar un body claro con la password:

```json
{
  "password": "contrasena_actual"
}
```

### `DELETE /users/me`

Borra la cuenta del usuario autenticado. Mantiene compatibilidad REST con metodo `DELETE`, pero tambien espera la contrasena actual en el body.

Requiere:

```text
Authorization: Bearer <idToken>
```

Recibe:

```json
{
  "password": "contrasena_actual"
}
```

Funcionamiento:

1. Valida token de Firebase.
2. Verifica la contrasena contra Firebase Authentication.
3. Borra el usuario en Firebase Authentication.
4. Borra el perfil `usuarios/{uid}` en Firestore.
5. Borra las transacciones y bonos asociados al usuario.

Respuesta orientativa:

```json
{
  "message": "Cuenta borrada correctamente.",
  "deleted_transactions": 12,
  "deleted_bonds": 3
}
```

### `GET /users/me/portfolio/gains`

Devuelve las ganancias totales y diarias de la cartera del usuario autenticado.

Tambien devuelve el valor y coste por cada posicion dentro de `positions`.

Requiere:

```text
Authorization: Bearer <idToken>
```

Respuesta orientativa:

```json
{
  "costBasisSource": "history",
  "dailyGain": -0.06,
  "hasCostBasis": true,
  "investedCost": 10.0,
  "positions": {
    "AAPL": {
      "costBasisSource": "history",
      "dailyGain": 0.42,
      "hasCostBasis": true,
      "investedCost": 44.10,
      "totalGain": 1.72,
      "totalValue": 45.82
    }
  },
  "source": "yfinance",
  "totalGain": 0.02,
  "totalValue": 10.02
}
```

`costBasisSource` indica como se calculo el dinero invertido:

```text
history          -> historial real de transacciones
balance_estimate -> estimacion con saldo inicial menos saldo actual
none             -> no calculable
```

`positions[ticker].totalValue` se usa en el frontend como `Valor actual` del activo seleccionado:

```text
valor actual = unidades en cartera * ultimo precio real
```

### `POST /users/me/portfolio/buy`

Compra un activo desde la pantalla de mercado.

Requiere:

```text
Authorization: Bearer <idToken>
```

Recibe dinero a invertir, no numero de acciones:

```json
{
  "ticker": "AAPL",
  "amount": 10
}
```

Funcionamiento:

1. Valida token de Firebase.
2. Valida que `ticker` exista y que `amount` sea mayor que 0.
3. Obtiene el ultimo precio real con `ApiHandler.obtener_tendencia(ticker, "1d")`.
4. Calcula unidades:

```text
quantity = amount / price
```

5. Llama a `DbHandler.realizar_compra(...)`.
6. Devuelve usuario actualizado.

Respuesta orientativa:

```json
{
  "message": "Compra realizada correctamente.",
  "operation": {
    "ticker": "AAPL",
    "quantity": 0.034,
    "price": 291.23,
    "total": 10,
    "balance": 990
  },
  "user": {}
}
```

### `POST /users/me/portfolio/sell`

Vende un porcentaje de un activo desde la pantalla de cartera.

Requiere:

```text
Authorization: Bearer <idToken>
```

Recibe:

```json
{
  "ticker": "AAPL",
  "percentage": 25
}
```

Funcionamiento:

1. Valida token de Firebase.
2. Valida que `ticker` exista y que `percentage` este entre 0 y 100.
3. Lee la cantidad actual del activo en la cartera del usuario.
4. Obtiene el ultimo precio real con `ApiHandler.obtener_tendencia(ticker, "1d")`.
5. Calcula unidades a vender:

```text
quantity = current_quantity * (percentage / 100)
```

6. Llama a `DbHandler.realizar_venta(...)`.
7. Devuelve usuario actualizado.

Respuesta orientativa:

```json
{
  "message": "Venta realizada correctamente.",
  "operation": {
    "ticker": "AAPL",
    "quantity": 0.038,
    "percentage": 25,
    "price": 300.15,
    "total": 11.40,
    "balance": 1001.40
  },
  "user": {}
}
```

El importe final de la venta puede variar ligeramente respecto al valor visto en pantalla, porque el backend consulta precio real en el momento de ejecutar la operacion.

### `GET /market/{ticker}/trend?range=1d|1w|1y`

Devuelve la tendencia historica de un activo para la grafica del frontend.

## Piezas importantes

### `resolve_email(email, username)`

Resuelve el email real de autenticacion. Se usa para mantener compatibilidad con el frontend actual, que todavia usa un campo llamado `username` aunque en realidad ahora contiene un email.

### `resolve_display_name(username, email)`

Genera un nombre visible para Firebase Auth. Si el valor recibido es un email, toma la parte anterior a `@`.

### `firebase_sign_in(email, password)`

Llama a Firebase Authentication usando `accounts:signInWithPassword`. Esta es la pieza que hace que el login ya no dependa de Firestore.

### `verify_current_user(authorization)`

Valida un `ID token` recibido en la cabecera `Authorization`.

### `calcular_costes_abiertos(transacciones)`

Calcula el coste invertido todavia abierto por activo. Usa compras y ventas para saber cuanto dinero queda invertido en las posiciones actuales.

Si no hay historial valido, el endpoint de ganancias usa una estimacion basada en saldo inicial de 1000 $ mas los depositos registrados menos saldo actual.

### `calcular_fondos_anadidos(transacciones)`

Ajusta el fallback de ganancias segun movimientos de saldo:

- suma `DEPOSITO`
- resta `RETIRADA`
- resta `BONO_INVERSION`
- suma `BONO_CIERRE`
- reinicia el ajuste con `REINICIO`

Esto evita que los bonos temporales se confundan con coste abierto de acciones.

### `BuyRequest`

Modelo Pydantic para la compra desde mercado. Usa:

- `ticker`
- `amount`

Se eligio `amount` porque el usuario introduce dinero a invertir. El backend calcula las unidades internamente.

### `SellRequest`

Modelo Pydantic para la venta desde cartera. Usa:

- `ticker`
- `percentage`

Se eligio `percentage` porque en cartera el usuario reduce una posicion existente. El backend calcula las unidades y el importe internamente.

### `SettingsRequest`

Modelo Pydantic para la configuracion. Usa:

- `theme`

Se guarda en Firestore dentro del perfil del usuario como `settings.theme`.

### `AddFundsRequest`

Modelo Pydantic para anadir fondos. Usa:

- `amount`
- `cantidad`
- `value`

El backend redondea a dos decimales, acepta numeros como texto y registra el ingreso como `DEPOSITO` para que el saldo sea auditable.

El frontend consume este endpoint desde `ConfiguracionSection`, no desde mercado, porque anadir saldo es una operacion de cuenta.

### `BondInvestmentRequest`

Modelo Pydantic para invertir en bonos. Usa:

- `ticker`
- `amount`

El backend calcula internamente `profit`, `payout`, `startedAt`, `maturityAt` y `secondsRemaining`.

El frontend puede mandar `amount` como numero o texto; el backend lo normaliza con la misma funcion usada para fondos.

## Como funciona a nivel de seguridad

- El registro y el login reales ya no usan la coleccion `usuarios` para validar contrasenas.
- La contraseña vive en Firebase Authentication.
- Firestore solo guarda el perfil y los datos de negocio.
- Las rutas protegidas usan `ID tokens` verificados por backend.

## Por que esta hecho asi

- Se usa FastAPI porque el codigo sigue siendo legible y el backend queda mas ordenado para el frontend.
- Se usa Firebase Authentication porque es mas seguro que guardar y comparar passwords en Firestore.
- Se mantiene compatibilidad con el formulario actual del frontend aceptando `username` como email para no forzar una ruptura brusca de la UI.
- Se devuelve `portfolio` como lista porque Angular lo recorre mejor que un diccionario crudo.
- Se mantiene separado el mercado en `ApiHandler` para no mezclar autenticacion con datos financieros.
- Se prioriza el historial real para ganancias y solo se usa estimacion si no hay datos suficientes.
- La compra se hace desde mercado porque el usuario ya esta viendo precio y tendencia del activo.
- La venta se hace desde cartera porque el usuario ya esta viendo sus posiciones reales.
- El frontend muestra `Valor actual` por activo usando `positions[ticker].totalValue`, no `investedCost`, porque para vender interesa el valor de mercado actual.
- La configuracion de tema se expone desde backend para que el modo claro/oscuro no dependa solo del navegador local.
- Los depositos se tratan como transacciones porque afectan al saldo y tambien al fallback de ganancias basado en saldo.
- Las retiradas y los reinicios tambien se registran como transacciones porque afectan al saldo y al calculo de ganancias.
- Las inversiones y cierres de bonos tambien ajustan ese fallback para que una posicion de bonos no parezca coste invertido en acciones.
- Los bonos usan una coleccion propia `bonos` porque tienen estado, vencimiento y liquidacion; el historial solo guarda el rastro financiero.

## Consideraciones

- El campo visual del frontend ya representa un email, aunque internamente se siga llamando `username` en algunos sitios.
- El backend necesita `FIREBASE_WEB_API_KEY` para el login contra Firebase Auth.
- Esa clave no debe quedar hardcodeada en el repositorio. Debe vivir en `.env` o en el sistema de secretos del entorno.
- La documentacion interactiva de FastAPI sigue disponible en `/docs`.
- El borrado de cuenta es irreversible: borra Firebase Authentication, perfil de Firestore y transacciones. Debe probarse solo con cuentas de prueba.
- La liquidacion de bonos ocurre cuando el frontend consulta o llama a liquidar; no hay un worker de fondo levantado por separado.
- El frontend usa `maturityAt` para el contador y llama a `POST /users/me/bonds/settle` al detectar bonos vencidos. `GET /users/me/bonds` tambien liquida vencidos para cubrir recargas o entradas tardias a la pantalla.
