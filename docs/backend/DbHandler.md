# DbHandler

Archivo fuente: [services/db_handler.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/db_handler.py)

## Proposito

`DbHandler` centraliza la conexion con Firebase Firestore y las operaciones principales de persistencia del backend: precios de mercado, registro e inicio de sesion de usuarios, lectura de usuario y movimientos de cartera.

## Dependencias

- Libreria externa: `firebase-admin`
- Libreria estandar: `hashlib`
- Credencial necesaria: ruta valida al archivo `service_account.json`
- Servicio externo: Firebase Firestore

## Constructor

### `__init__(certificado_path)`

Inicializa Firebase usando un certificado de servicio y crea el cliente de Firestore.

### Parametros

- `certificado_path`: ruta al JSON de credenciales de Firebase.

## Metodos

### `actualizar_precio(datos)`

Actualiza en la coleccion `mercado` el documento asociado al simbolo recibido.

### Parametros

- `datos`: diccionario generado por `ApiHandler`, con claves como `simbolo`, `precio`, `variacion` y `porcentaje`.

### Efecto

Escribe en Firestore campos como:

- `precio_actual`
- `cambio`
- `porcentaje`
- `ultima_actualizacion`

### `_encriptar_password(password)`

Genera un hash SHA-256 de la contrasena para evitar guardarla en texto plano.

### `crear_usuario(username, password)`

Crea un documento nuevo en la coleccion `usuarios` si el nombre de usuario no existe todavia.

### Parametros

- `username`: nombre elegido por el usuario.
- `password`: contrasena introducida por el usuario.

### Retorno

Devuelve una tupla:

```python
(exito, resultado)
```

Si la operacion va bien, `resultado` contiene el `user_id`.

### Estructura guardada

Los usuarios nuevos se almacenan con este formato general:

```python
{
    "username": "nombre_visible",
    "password": "hash_sha256",
    "saldo": 1000.0,
    "cartera": {},
    "fecha_creacion": firestore.SERVER_TIMESTAMP
}
```

### `autenticar_usuario(username, password)`

Comprueba si existe el usuario y si la contrasena coincide con el hash guardado en Firestore.

### Parametros

- `username`: nombre del usuario.
- `password`: contrasena en texto introducida en el login.

### Retorno

Devuelve una tupla:

```python
(exito, resultado)
```

Si la operacion va bien, `resultado` contiene el `user_id`.

### `obtener_usuario(user_id="usuario_demo")`

Lee un usuario desde la coleccion `usuarios`. Si faltan campos como `saldo` o `cartera`, los completa en memoria. Si no existe, crea un usuario inicial con saldo `1000.0` y cartera vacia.

### Parametros

- `user_id`: identificador del usuario a consultar.

### Retorno

Devuelve un diccionario con los datos del usuario.

### `realizar_compra(ticker, cantidad, precio_unidad, user_id="usuario_demo")`

Comprueba si el usuario tiene saldo suficiente y, en caso afirmativo, descuenta el importe y suma la cantidad comprada a la cartera.

### Parametros

- `ticker`: activo a comprar.
- `cantidad`: unidades del activo.
- `precio_unidad`: precio de compra por unidad.
- `user_id`: usuario sobre el que se opera.

### Retorno

Devuelve una tupla:

```python
(exito, saldo_resultante)
```

Tambien registra la operacion en la coleccion `transacciones`.

### `realizar_venta(ticker, cantidad_a_vender, precio_unidad, user_id="usuario_demo")`

Valida que el usuario tenga suficientes unidades, calcula el ingreso y actualiza saldo y cartera.

### Parametros

- `ticker`: activo a vender.
- `cantidad_a_vender`: unidades a retirar de la cartera.
- `precio_unidad`: precio usado para calcular el ingreso.
- `user_id`: usuario sobre el que se opera.

### Retorno

Devuelve una tupla:

```python
(exito, saldo_resultante)
```

Tambien registra la operacion en la coleccion `transacciones`.

### `obtener_historial(user_id)`

Consulta las ultimas transacciones del usuario, ordenadas por fecha descendente.

## Uso dentro del proyecto

- [main.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/main.py): lectura de saldo, cartera, compras y ventas.
- [main.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/main.py): registro, login, logout, lectura de saldo, cartera, compras y ventas.
- [services/worker_precios.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/worker_precios.py): persistencia periodica de precios en `mercado`.

## Consideraciones

- Si `certificado_path` no existe o no apunta a un JSON valido, la inicializacion de Firebase falla.
- La clase accede directamente a colecciones concretas: `mercado` y `usuarios`.
- Tambien usa la coleccion `transacciones` para el historial de movimientos.
- La contrasena se almacena como hash SHA-256, no en texto plano.
- Sigue siendo una autenticacion sencilla para aprendizaje; no sustituye a Firebase Authentication ni a un sistema de seguridad mas robusto.
- Los errores se imprimen por consola y no se relanzan.

## Por que esta hecho asi

- Se centraliza Firestore en una sola clase para que el resto del proyecto no tenga que repetir consultas ni rutas de colecciones.
- Se usa SHA-256 porque es una mejora simple frente a guardar contrasenas en texto plano y mantiene el codigo facil de entender.
- No se ha usado Firebase Authentication porque el objetivo actual es tener un flujo de usuarios sencillo y totalmente visible en el codigo del proyecto.
- Se usa el nombre de usuario en minusculas como `user_id` para evitar duplicados por mayusculas y simplificar las busquedas.
- Se registra cada compra y venta en `transacciones` para poder mostrar historial sin recalcularlo desde la cartera.
