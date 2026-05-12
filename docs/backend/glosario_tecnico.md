# Glosario tecnico del BackEnd

Este documento explica palabras tecnicas que aparecen en el backend de Simtrade-BackEnd. La idea es que el equipo pueda entender no solo que significa cada termino, sino tambien por que se usa aqui y por que no se eligio otro enfoque.

## API

Una API es una forma de comunicar dos programas entre si. En este proyecto, el frontend llama al backend mediante rutas HTTP.

### Por que se usa

Se usa porque el frontend necesita pedir datos y enviar acciones al backend de una forma ordenada.

### Por que no otro metodo

No se accede directamente a Firestore desde el frontend porque asi concentramos la logica sensible en el backend y mantenemos una sola capa de reglas.

## REST

REST es una forma comun de organizar rutas HTTP usando recursos y metodos como `GET` o `POST`.

### Por que se usa

Se usa porque hace que las rutas sean faciles de entender desde frontend y backend.

### Por que no otro metodo

No se ha usado algo mas complejo como GraphQL porque el proyecto actual necesita pocas rutas y respuestas muy concretas.

## Endpoint

Un endpoint es una ruta concreta de la API, por ejemplo `GET /users/{username}/portfolio`.

### Por que se usa

Permite separar cada accion del sistema en una URL clara.

### Por que no otro metodo

No se mete toda la logica en una sola ruta porque eso haria mas dificil entender y mantener el backend.

## Payload

El payload es el contenido que viaja dentro de una peticion o respuesta. En login y registro, el payload suele llevar `username` y `password`.

### Por que se usa

Se usa porque el backend necesita recibir datos estructurados desde el frontend.

### Por que no otro metodo

No se usan parametros sueltos en la URL para usuario y contrasena porque los datos de acceso deben viajar en el cuerpo de la peticion y no en la direccion.

## AuthRequest

`AuthRequest` es el modelo de datos que define como debe llegar una peticion de autenticacion en [api_server.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/api_server.py:1).

### Por que se usa

Se usa para validar automaticamente que llegan los campos `username` y `password`.

### Por que no otro metodo

No se trabaja con diccionarios crudos en FastAPI porque un modelo hace el codigo mas claro y reduce errores de validacion manual.

## FastAPI

FastAPI es el framework que usamos para crear la API REST del backend.

### Por que se usa

Se usa porque mantiene el codigo sencillo, valida datos de entrada y genera documentacion automatica en `/docs`.

### Por que no otro metodo

No se mantiene `http.server` porque era mas manual para manejar rutas, validacion y respuestas. Tampoco se ha usado algo mas grande como Django porque seria excesivo para este backend.

## CORS

CORS son reglas que controlan desde que origen web se puede llamar a la API.

### Por que se usa

Se usa porque el frontend corre en `localhost:4200` y el navegador necesita permiso para hablar con el backend.

### Por que no otro metodo

No se deja abierto a cualquier origen porque es mejor limitarlo al entorno de desarrollo que realmente usa el proyecto.

## HTTPException

`HTTPException` es la forma que usa FastAPI para responder con errores HTTP como `400`, `401` o `409`.

### Por que se usa

Se usa porque deja claro el motivo del error y el codigo de respuesta adecuado.

### Por que no otro metodo

No se devuelve siempre `200` con mensajes de error porque eso confunde al frontend y rompe el significado normal de HTTP.

## Status code

El status code es el numero que acompana a la respuesta HTTP, por ejemplo `200`, `201`, `400` o `401`.

### Por que se usa

Se usa para que el frontend sepa rapidamente si una operacion ha ido bien o mal.

### Por que no otro metodo

No se depende solo del texto del mensaje porque los codigos HTTP son un estandar mas claro para integrar sistemas.

## Firestore

Firestore es la base de datos en la nube donde se guardan usuarios, mercado y transacciones.

### Por que se usa

Se usa porque encaja bien con documentos JSON-like y simplifica guardar estructuras como cartera o historial.

### Por que no otro metodo

No se ha usado una base de datos relacional porque el proyecto actual funciona bien con documentos simples y acceso rapido a colecciones.

## Coleccion

Una coleccion en Firestore agrupa documentos del mismo tipo, por ejemplo `usuarios`, `mercado` o `transacciones`.

### Por que se usa

Se usa para organizar la informacion por tipo de dato.

### Por que no otro metodo

No se guarda todo en una sola coleccion porque seria mucho menos claro separar usuarios, activos y movimientos.

## Documento

Un documento es una unidad de datos dentro de una coleccion de Firestore.

### Por que se usa

Se usa porque cada usuario, activo o transaccion puede representarse como una entidad independiente.

### Por que no otro metodo

No se trabaja con un unico gran documento global porque eso haria mas dificil actualizar datos concretos y escalar el proyecto.

## DbHandler

`DbHandler` es la clase que centraliza el acceso a Firestore.

### Por que se usa

Se usa para tener un unico punto del backend que conoce colecciones, consultas y actualizaciones.

### Por que no otro metodo

No se hacen consultas de Firestore repartidas por todos los archivos porque eso duplicaria codigo y mezclaria responsabilidades.

## ApiHandler

`ApiHandler` es la clase que centraliza el acceso a Finnhub.

### Por que se usa

Se usa para aislar las llamadas a mercado del resto del backend.

### Por que no otro metodo

No se llama a Finnhub directamente desde `main.py` o desde el worker porque es mejor encapsular esa logica en una sola clase.

## Ticker

Un ticker es el identificador corto de un activo financiero, por ejemplo `AAPL` o `TSLA`.

### Por que se usa

Se usa porque es la forma normal de identificar acciones o activos en APIs de mercado.

### Por que no otro metodo

No se usan nombres largos como "Apple Inc." porque las APIs financieras trabajan mejor con simbolos normalizados y unicos.

## Portfolio

Portfolio o cartera es el conjunto de activos que posee un usuario.

### Por que se usa

Se usa porque representa de forma directa las posiciones compradas por el usuario.

### Por que no otro metodo

No se recalcula siempre desde historial porque guardar la cartera actual permite consultar mas rapido el estado del usuario.

## Historial de transacciones

Es el registro de compras y ventas realizadas por un usuario.

### Por que se usa

Se usa para que el usuario pueda ver que operaciones ha hecho y cuando.

### Por que no otro metodo

No se guarda solo el saldo final porque eso haria imposible explicar o auditar como se ha llegado a ese resultado.

## SHA-256

SHA-256 es una funcion hash que transforma una contrasena en una cadena irreconocible a simple vista.

### Por que se usa

Se usa para no guardar la contrasena en texto plano y mantener una mejora de seguridad sencilla.

### Por que no otro metodo

No se guarda la contrasena tal cual porque seria inseguro. Tampoco se ha usado `bcrypt` de momento porque se busco una solucion mas simple y facil de entender para este proyecto academico.

## User ID

El `user_id` es el identificador interno del usuario dentro de Firestore.

### Por que se usa

Se usa para localizar el documento del usuario de forma estable.

### Por que no otro metodo

No se usa directamente el nombre con mayusculas y espacios tal como lo escribe el usuario porque normalizarlo en minusculas evita duplicados y simplifica las consultas.

## Middleware

Un middleware es una capa intermedia que se ejecuta antes o despues de las rutas. En este backend se usa para CORS.

### Por que se usa

Se usa para aplicar reglas comunes a toda la API sin repetir codigo en cada endpoint.

### Por que no otro metodo

No se anaden cabeceras manualmente en cada ruta porque eso seria repetitivo y mas propenso a errores.

## Uvicorn

Uvicorn es el servidor que ejecuta la aplicacion FastAPI.

### Por que se usa

Se usa porque es la forma habitual y sencilla de arrancar una app FastAPI.

### Por que no otro metodo

No se usa un servidor mas complejo porque para desarrollo y para el alcance actual del proyecto no hace falta.

## yfinance

`yfinance` es una libreria Python que permite consultar datos de mercado historicos desde Yahoo Finance.

### Por que se usa

Se usa para obtener puntos reales de precio y pintar graficas de tendencia en la cartera.

### Por que no otro metodo

No se implemento una integracion manual de velas porque seria mas larga y menos clara para el estado actual del proyecto.

## Historico de mercado

El historico de mercado es una lista de precios en distintos momentos.

### Por que se usa

Se usa para mostrar si una accion ha subido o bajado en un rango de tiempo.

### Por que no otro metodo

No basta con el precio actual, porque una grafica necesita varios puntos para dibujar una tendencia.

## Cache

Una cache guarda temporalmente una respuesta para no pedirla de nuevo cada vez.

### Por que se menciona

Ahora mismo el backend no cachea historicos. Cada peticion de tendencia pide datos al proveedor.

### Por que no se ha hecho todavia

Se priorizo una implementacion sencilla y clara. La cache puede anadirse despues si hay muchas peticiones o problemas de rendimiento.

## Coste abierto

El coste abierto es el dinero invertido que todavia corresponde a posiciones que siguen en cartera.

### Por que se usa

Se usa para calcular ganancias totales:

```text
ganancia total = valor actual - coste abierto
```

### Por que no otro metodo

No basta con mirar solo el saldo porque puede haber ventas parciales. El historial permite calcular cuanto coste queda asociado a las acciones que aun se conservan.

## Ganancia diaria

La ganancia diaria es el cambio de valor durante el dia actual.

### Por que se usa

Sirve para saber si la cartera ha subido o bajado hoy.

### Por que no sustituye a la ganancia total

Porque compara contra el inicio del dia, no contra el precio de compra.

## Ganancia total

La ganancia total es lo ganado o perdido desde la compra o desde el coste invertido calculado.

### Por que se usa

Sirve para saber si la inversion completa va en positivo o negativo.

### Por que puede diferir de la diaria

Una posicion puede ir ganando en total pero haber bajado durante el dia, o al reves.
