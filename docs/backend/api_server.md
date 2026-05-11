# api_server

Archivo fuente: [api_server.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/api_server.py)

## Proposito

`api_server.py` expone una API REST minima con FastAPI para que el frontend pueda registrar usuarios, iniciar sesion, consultar cartera y obtener tendencias reales de mercado.

## Responsabilidad dentro del sistema

Este script actua como puente entre el frontend y la logica del backend. Su trabajo es recibir peticiones HTTP, validar datos basicos y devolver respuestas JSON sencillas.

## Dependencias

- Libreria estandar: `os`
- Libreria externa: `python-dotenv`
- Libreria externa: `fastapi`
- Libreria externa: `uvicorn`
- Libreria externa: `pydantic`
- Clase interna:
  - [DbHandler](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/DbHandler.md)
  - [ApiHandler](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/ApiHandler.md)

## Variables de entorno usadas

- `FIREBASE_JSON_PATH`
- `SIMTRADE_API_HOST`
- `SIMTRADE_API_PORT`

## Configuracion base

- Host por defecto: `127.0.0.1`
- Puerto por defecto: `8000`
- Origenes permitidos por defecto:
  - `http://127.0.0.1:4200`
  - `http://localhost:4200`

## Endpoints disponibles

### `POST /auth/login`

Recibe:

```json
{
  "username": "usuario",
  "password": "clave"
}
```

Si las credenciales son correctas, devuelve un JSON con mensaje y datos publicos del usuario.

### `POST /auth/register`

Recibe:

```json
{
  "username": "usuario",
  "password": "clave"
}
```

Si el usuario no existe, lo crea en Firestore y devuelve sus datos publicos.

### `GET /users/{username}/portfolio`

Devuelve la cartera del usuario en un formato simple para poder recorrerla e imprimirla en el frontend.

Respuesta orientativa:

```json
{
  "user": {
    "id": "daniel",
    "username": "Daniel",
    "saldo": 1000.0,
    "cartera": {
      "AAPL": 2.5
    }
  },
  "portfolio": [
    {
      "ticker": "AAPL",
      "cantidad": 2.5
    }
  ],
  "total_activos": 1
}
```

### `GET /market/{ticker}/trend`

Devuelve puntos historicos reales de un activo para pintar una grafica en el frontend.

Ejemplos:

```text
GET /market/AAPL/trend?range=1d
GET /market/AAPL/trend?range=1w
GET /market/AAPL/trend?range=1y
```

Rangos permitidos:

- `1d`: un dia
- `1w`: una semana de mercado
- `1y`: un ano

Respuesta orientativa:

```json
{
  "ticker": "AAPL",
  "range": "1d",
  "points": [
    {
      "timestamp": 1778506200,
      "price": 291.23
    }
  ],
  "source": "yfinance"
}
```

Si el rango no es valido devuelve `400`. Si no hay datos reales para ese activo devuelve `404`.

### `OPTIONS`

FastAPI y el middleware CORS responden automaticamente a las peticiones preflight del navegador.

## Funciones y piezas importantes

### `public_user(user_id)`

Construye una version segura del usuario para devolverla al frontend sin incluir la contrasena.

### `AuthRequest`

Modelo de entrada para validar `username` y `password` en login y registro.

### `app`

Instancia principal de FastAPI donde se registran las rutas y el middleware CORS.

## Flujo de ejecucion

1. Carga variables de entorno.
2. Crea una instancia global de `DbHandler`.
3. Configura FastAPI y el middleware CORS.
4. Arranca Uvicorn en el host y puerto configurados.
5. Espera peticiones del frontend.
6. Segun la ruta:
   - devuelve la cartera de un usuario
   - devuelve la tendencia de mercado de un ticker
   - autentica al usuario
   - registra al usuario
   - o devuelve el estado basico de la API

## Por que esta hecho asi

- Se usa FastAPI porque mantiene el codigo claro pero da una estructura REST mas limpia, validacion automatica y mejor integracion con frontend.
- Se reutiliza `DbHandler` para no duplicar la logica de usuarios entre consola y API.
- Se devuelve un usuario publico sin password porque el frontend solo necesita identidad, saldo y cartera.
- Se devuelve tambien `portfolio` como lista de posiciones porque en frontend es mas comodo recorrer una lista para imprimir que un diccionario crudo.
- La transformacion de cartera vive en `DbHandler` y no en la ruta para mantener `api_server.py` centrado en HTTP y no en logica de datos.
- La tendencia de mercado vive en `ApiHandler` para mantener separada la logica de proveedores externos.
- Se ha limitado CORS a `localhost:4200` porque el frontend actual trabaja en desarrollo desde Angular en ese puerto.
- Se usan endpoints pequenos y directos porque ahora mismo el objetivo es cubrir login, registro y consulta de cartera sin construir una API completa antes de tiempo.

## Consideraciones

- Este servidor no implementa tokens, sesiones ni refresco de autenticacion.
- La seguridad esta pensada para un proyecto academico y de aprendizaje, no para produccion.
- Si Firestore no esta disponible o faltan variables de entorno, las peticiones no funcionaran correctamente.
- Si el proveedor de mercado no reconoce el ticker, la ruta de tendencia devolvera `404`.
- La documentacion interactiva de FastAPI queda disponible por defecto en `/docs`.
