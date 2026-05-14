# DbHandler

Archivo fuente: [services/db_handler.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/db_handler.py)

## Proposito

`DbHandler` centraliza el acceso a Firestore para los datos de negocio del proyecto.

## Que guarda ahora mismo

La coleccion `usuarios` ya no se usa para autenticar contrasenas. Su funcion actual es guardar:

- `username`
- `email`
- `saldo`
- `cartera`
- `settings`
- `fecha_creacion`
- `auth_provider`

Ejemplo:

```python
{
    "username": "monsunodaniel",
    "email": "monsunodaniel@gmail.com",
    "saldo": 1000.0,
    "cartera": {},
    "settings": {
        "theme": "light"
    },
    "fecha_creacion": firestore.SERVER_TIMESTAMP,
    "auth_provider": "firebase_auth"
}
```

## Metodos principales

### `crear_perfil_auth(uid, email, username)`

Crea o actualiza el perfil del usuario en `usuarios/{uid}` despues de que Firebase Authentication haya creado la cuenta.

### `obtener_usuario(user_id)`

Lee un usuario desde Firestore.

### `obtener_cartera(user_id)`

Transforma la cartera del usuario a una lista de posiciones:

```python
[
    {"ticker": "AAPL", "cantidad": 2.5}
]
```

### `obtener_perfil_publico(user_id)`

Devuelve un perfil seguro para respuestas de API.

### `obtener_configuracion(user_id)`

Lee las preferencias del usuario. Actualmente normaliza y devuelve:

```python
{
    "theme": "light"
}
```

Si el documento antiguo no tiene configuracion, devuelve `light` como valor por defecto.

### `actualizar_tema(user_id, theme)`

Actualiza `settings.theme` con `dark` o `light`.

### `anadir_fondos(user_id, cantidad)`

Suma la cantidad al `saldo`, redondea a dos decimales y registra un movimiento `DEPOSITO` en `transacciones`.

El deposito se registra con `ticker = "CASH"`, `cantidad = 1`, `precio_unidad = cantidad` y `total_dinero = cantidad`. Asi el historial puede mostrar el ingreso y el calculo de ganancias puede distinguir dinero anadido frente a dinero generado por ventas.

### `eliminar_cuenta(user_id)`

Borra el documento del usuario en `usuarios/{uid}` y elimina sus documentos de `transacciones`.

El borrado de Firebase Authentication se hace en `api_server.py`; `DbHandler` se ocupa de limpiar los datos de negocio en Firestore.

### `actualizar_precio(datos)`

Actualiza la coleccion `mercado` con precios sincronizados.

### `realizar_compra(...)`

Actualiza saldo, cartera y registra la compra en `transacciones`.

En la web, este metodo se llama desde `POST /users/me/portfolio/buy`. El frontend envia dinero a invertir y el backend calcula las unidades antes de llamar a `realizar_compra`.

### `realizar_venta(...)`

Actualiza saldo, cartera y registra la venta en `transacciones`.

### `obtener_historial(user_id)`

Consulta las ultimas transacciones del usuario.

Actualmente devuelve una lista de diccionarios ya ordenada de mas reciente a mas antigua y limitada a 20 movimientos. Cada elemento incluye el `id` del documento para que el frontend pueda usarlo como clave estable.

### `obtener_transacciones_usuario(user_id)`

Devuelve todas las transacciones del usuario para calcular ganancias.

Primero consulta por usuario y despues ordena en Python por `fecha`. Se hizo asi para evitar depender de indices compuestos de Firestore al ordenar directamente en la query.

## Por que esta hecho asi

- Firestore se queda solo con datos de negocio, no con la responsabilidad de autenticar.
- El documento del usuario usa el `uid` de Firebase Authentication, que es estable y seguro.
- La cartera se transforma en lista dentro del backend para no obligar al frontend a reinterpretar estructuras de Firestore.
- Las transacciones se usan para calcular el coste invertido real antes de recurrir a estimaciones.
- Los depositos se guardan como transacciones para que el saldo no cambie sin rastro.
- Los depositos tambien evitan que el fallback de ganancias confunda fondos anadidos con dinero no invertido.
- Se mantiene `DbHandler` como punto unico de acceso para que la logica de base de datos no se disperse en toda la aplicacion.

## Seguridad

- El documento ya no guarda el password ni en texto plano ni en hash.
- El acceso a cartera y perfil debe apoyarse en el `uid` autenticado por token.
- Los datos sensibles de identidad quedan delegados en Firebase Authentication.
