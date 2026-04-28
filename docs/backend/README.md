# Documentacion de clases Python del BackEnd

Esta carpeta contiene la documentacion funcional de todas las clases Python que forman el backend actual de Simtrade-BackEnd.

## Clases documentadas

- [ApiHandler](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/ApiHandler.md)
- [DbHandler](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/DbHandler.md)
- [worker_precios](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/worker_precios.md)

## Cobertura actual

Tras revisar los archivos Python del repositorio, actualmente solo existen estas dos clases:

- `ApiHandler`
- `DbHandler`

No se han encontrado mas declaraciones `class` en otros modulos Python del proyecto.

## Scripts documentados

Los siguientes archivos forman parte del flujo del backend y tienen documentacion propia aunque no definan clases:

- [main.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/main.py): punto de entrada de la aplicacion de usuario.
- [services/worker_precios.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/worker_precios.py): worker que sincroniza precios desde Finnhub hacia Firestore.

## Resumen de arquitectura

- `ApiHandler` centraliza la lectura de precios desde Finnhub.
- `DbHandler` centraliza la conexion y las operaciones contra Firestore.
- `worker_precios.py` usa ambas clases para mantener actualizado el mercado.
- `main.py` usa `DbHandler` para mostrar mercado, cartera y operaciones de compra o venta.
