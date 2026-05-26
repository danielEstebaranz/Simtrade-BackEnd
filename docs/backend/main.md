# main

Archivo fuente: [main.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/main.py)

## Proposito

`main.py` es el punto de entrada de la aplicacion de consola. Sirve para probar el backend sin depender del frontend y permite iniciar sesion, registrarse, comprar, vender y consultar historial.

## Responsabilidad dentro del sistema

Este script conecta la interfaz de consola con dos capas distintas:

- Firebase Authentication para identidad y validacion de credenciales.
- Firestore, a traves de `DbHandler`, para perfil, saldo, cartera e historial.

Se ha separado asi porque autenticar y guardar datos de negocio son problemas distintos. Firebase resuelve mejor la seguridad del login y Firestore sigue siendo el lugar natural para guardar la operativa del simulador.

## Dependencias

- Libreria estandar: `os`
- Librerias externas:
  - `python-dotenv`
  - `firebase-admin`
  - `requests`
- Clase interna:
  - [DbHandler](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/DbHandler.md)

## Variables de entorno necesarias

- `FIREBASE_JSON_PATH`
- `FIREBASE_WEB_API_KEY`

## Funciones principales

### `resolver_email(email_o_usuario)`

Convierte la entrada del usuario en un email valido cuando el texto tiene formato de correo.

Se usa para mantener el flujo simple en consola: el usuario sigue viendo un campo tipo `Usuario`, pero el sistema exige realmente un email porque Firebase Authentication trabaja con email y password.

### `resolver_nombre_visible(email_o_usuario)`

Obtiene un nombre visible sencillo a partir del email.

Si el usuario escribe `monsunodaniel@gmail.com`, el nombre mostrado pasa a ser `monsunodaniel`. Se eligio este enfoque porque evita pedir un segundo campo extra en consola y mantiene el registro facil de entender.

### `iniciar_sesion_firebase(email, password)`

Llama a Firebase Authentication mediante `signInWithPassword` y devuelve:

- si el login fue correcto
- el `uid` del usuario autenticado

Se usa este metodo REST y no una comparacion manual en Firestore porque:

- Firebase ya valida credenciales de forma segura
- devuelve una identidad real del usuario
- evita guardar o comparar passwords en Firestore

### `mostrar_menu_login()`

Muestra el menu inicial con tres opciones:

- iniciar sesion
- registrarse
- salir

### `iniciar_sesion(db)`

Pide email y contraseña por consola, valida que el email tenga formato correcto y autentica contra Firebase Authentication.

Si el login es correcto, devuelve el `uid` del usuario para cargar su perfil desde Firestore.

### `registrarse(db)`

Crea el usuario en Firebase Authentication y, justo despues, crea su perfil en Firestore mediante `db.crear_perfil_auth(...)`.

Se hace en ese orden a proposito:

1. primero se crea la identidad real
2. despues se crea el perfil de negocio

Esto evita el error que salio durante la migracion, cuando podia existir un documento en Firestore sin un usuario real en Authentication.

### `autenticar_usuario(db)`

Mantiene al usuario dentro del menu de acceso hasta que:

- inicia sesion correctamente
- se registra correctamente
- o decide salir

### `mostrar_menu(saldo)`

Muestra el menu principal de la aplicacion autenticada con el saldo actual del usuario.

Las opciones actuales son:

- ver mercado e invertir
- ver mi cartera
- consultar transacciones
- cerrar sesion
- salir

### `app_usuario()`

Coordina todo el flujo principal del programa:

1. crea `DbHandler`
2. espera autenticacion
3. carga el perfil del usuario con su `uid`
4. permite comprar, vender y ver historial
5. vuelve al login si el usuario cierra sesion

## Flujo de ejecucion

1. Carga variables de entorno con `load_dotenv()`.
2. Crea una instancia de `DbHandler`.
3. Muestra el menu de acceso.
4. Si el usuario inicia sesion o se registra:
   - Firebase Authentication valida o crea la identidad
   - Firestore devuelve el perfil del `uid`
5. El usuario opera con mercado, cartera e historial.
6. Si elige `Cerrar sesion`, vuelve al menu de login.
7. Si elige `Salir`, termina el programa.

## Datos usados en Firestore

- Coleccion `usuarios`:
  - guarda `username`, `email`, `saldo`, `cartera`, `fecha_creacion` y `auth_provider`
  - el documento se identifica por `uid`
  - no guarda `password`
- Coleccion `mercado`:
  - lee `precio_actual` de los activos
- Coleccion `transacciones`:
  - consulta y escribe el historial del usuario autenticado

## Validaciones importantes

- En consola, el login exige un email valido.
- La contraseña de registro debe tener al menos 6 caracteres.

No se eligieron validaciones mas complejas porque el objetivo de esta app de consola es ser facil de seguir. Las reglas puestas son las minimas necesarias para encajar con Firebase Authentication y evitar errores frecuentes.

## Por que esta hecho asi

- Se mantiene una aplicacion de consola porque permite probar todo el backend aunque el frontend todavia no tenga todas las pantallas terminadas.
- Se usa Firebase Authentication para login y registro porque es mas seguro que guardar passwords en Firestore.
- Se usa Firestore solo para datos de negocio porque saldo, cartera e historial no forman parte de la identidad.
- Se sigue leyendo el mercado desde Firestore y no desde Finnhub en tiempo real para desacoplar la experiencia del usuario del proceso de sincronizacion.
- Se ha añadido `Cerrar sesion` para poder cambiar de usuario sin reiniciar el programa completo.

## Error importante resuelto durante la migracion

Durante la migracion completa se produjo este error:

```text
Error: El usuario no existe.
```

### Causa

La web ya usaba Firebase Authentication, pero `main.py` seguia intentando autenticar con el metodo antiguo `db.autenticar_usuario(...)`, que buscaba usuarios por `username` dentro de Firestore.

Como los perfiles nuevos ya se guardan por `uid` y sin `password`, la consola no podia encontrar al usuario y parecia que no existia.

### Solucion

Se sustituyo el login de consola por autenticacion real contra Firebase Authentication y despues se paso a leer el perfil desde Firestore con el `uid` devuelto por Firebase.
