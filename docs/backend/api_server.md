# api_server

Archivo fuente: [api_server.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/api_server.py)

## Proposito

`api_server.py` expone la API REST principal del backend. Gestiona autenticacion contra Firebase Authentication, consulta de perfil, cartera, ganancias y tendencia de mercado para el frontend.

## Responsabilidad dentro del sistema

Este archivo recibe las peticiones HTTP del frontend y coordina tres piezas:

- Firebase Authentication para registro e inicio de sesion
- Firestore para perfil, cartera, saldo e historial
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
4. Devuelve el usuario publico.

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

### `GET /users/me/portfolio/gains`

Devuelve las ganancias totales y diarias de la cartera del usuario autenticado.

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

Si no hay historial valido, el endpoint de ganancias usa una estimacion basada en saldo inicial de 1000 $ menos saldo actual.

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

## Consideraciones

- El campo visual del frontend ya representa un email, aunque internamente se siga llamando `username` en algunos sitios.
- El backend necesita `FIREBASE_WEB_API_KEY` para el login contra Firebase Auth.
- Esa clave no debe quedar hardcodeada en el repositorio. Debe vivir en `.env` o en el sistema de secretos del entorno.
- La documentacion interactiva de FastAPI sigue disponible en `/docs`.
