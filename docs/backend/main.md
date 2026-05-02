# main

Archivo fuente: [main.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/main.py)

## Proposito

`main.py` es el punto de entrada de la aplicacion de consola para el usuario final. Controla el flujo de acceso, el menu principal y las operaciones de consulta, compra, venta e historial.

## Responsabilidad dentro del sistema

Este script conecta la interfaz de consola con Firestore usando `DbHandler`. Primero gestiona el acceso del usuario y despues permite operar con el mercado ya sincronizado por el worker.

## Dependencias

- Libreria estandar: `os`
- Libreria externa: `python-dotenv`
- Clase interna:
  - [DbHandler](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/DbHandler.md)

## Variables de entorno necesarias

- `FIREBASE_JSON_PATH`

## Funciones principales

### `mostrar_menu_login()`

Muestra el menu inicial con tres opciones:

- iniciar sesion
- registrarse
- salir

### `iniciar_sesion(db)`

Pide usuario y contrasena por consola y valida el acceso llamando a `db.autenticar_usuario(...)`.

### `registrarse(db)`

Pide un nombre de usuario y una contrasena y crea el documento del usuario en Firestore llamando a `db.crear_usuario(...)`.

### `autenticar_usuario(db)`

Mantiene al usuario en el menu de acceso hasta que inicia sesion, se registra correctamente o decide salir.

### `mostrar_menu(saldo)`

Muestra el menu principal de la aplicacion autenticada con el saldo actual del usuario.

Las opciones actuales son:

- ver mercado e invertir
- ver mi cartera
- consultar transacciones
- cerrar sesion
- salir

### `app_usuario()`

Coordina todo el flujo principal del programa.

## Flujo de ejecucion

1. Carga variables de entorno con `load_dotenv()`.
2. Crea una instancia de `DbHandler`.
3. Muestra el menu de acceso.
4. Si el usuario se autentica:
   - carga sus datos desde Firestore
   - muestra el saldo
   - permite comprar, vender y consultar transacciones
5. Si el usuario elige `Cerrar sesion`, vuelve al menu de login.
6. Si el usuario elige `Salir`, termina el programa.

## Datos usados en Firestore

- Coleccion `usuarios`:
  - guarda `username`, `password`, `saldo`, `cartera` y `fecha_creacion`
- Coleccion `mercado`:
  - lee `precio_actual` de los activos
- Coleccion `transacciones`:
  - consulta el historial del usuario autenticado

## Consideraciones

- La autenticacion es sencilla y esta pensada para ser facil de entender.
- La contrasena se transforma con SHA-256 antes de guardarse.
- El script depende de que el worker haya actualizado precios en la coleccion `mercado`.
- El mercado mostrado al usuario se limita a los tickers definidos en el propio script.

## Por que esta hecho asi

- Se ha hecho una aplicacion de consola porque permite probar todo el flujo del backend sin depender del frontend.
- El login y el registro se resuelven en menus separados para que el flujo sea mas claro para quien este aprendiendo el proyecto.
- Se usa `DbHandler` para todas las operaciones de usuario en vez de acceder a Firestore directamente desde el menu.
- Se consulta el mercado desde Firestore y no desde Finnhub en tiempo real para desacoplar la experiencia del usuario del proceso de sincronizacion.
- Se ha anadido `Cerrar sesion` para poder cambiar de usuario sin reiniciar el programa completo.
