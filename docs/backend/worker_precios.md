# worker_precios

Archivo fuente: [services/worker_precios.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/worker_precios.py)

## Proposito

`worker_precios.py` es un script de backend encargado de sincronizar precios de mercado desde Finnhub hacia Firebase Firestore de forma periodica.

## Responsabilidad dentro del sistema

Este worker mantiene actualizada la coleccion `mercado` en Firestore para que la aplicacion principal pueda consultar precios desde la base de datos sin llamar directamente a la API externa en cada operacion del usuario.

## Dependencias

- Libreria estandar: `os`, `time`
- Libreria externa: `python-dotenv`
- Clases internas:
  - [ApiHandler](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/ApiHandler.md)
  - [DbHandler](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/docs/backend/DbHandler.md)

## Variables de entorno necesarias

- `FINNHUB_API_KEY`
- `FIREBASE_JSON_PATH`

## Funcion principal

### `ejecutar_worker()`

Inicializa los servicios, define la lista de activos a sincronizar y entra en un bucle infinito que actualiza precios cada cierto intervalo.

## Flujo de ejecucion

1. Carga variables de entorno con `load_dotenv()`.
2. Crea una instancia de `ApiHandler` con la API key de Finnhub.
3. Crea una instancia de `DbHandler` con la ruta al certificado de Firebase.
4. Define la lista de activos a consultar:
   - `AAPL`
   - `TSLA`
   - `AMZN`
   - `MSFT`
   - `BINANCE:BTCUSDT`
5. Define un intervalo de 60 segundos.
6. En cada iteracion:
   - consulta el precio de cada activo con `api.obtener_precio_actual(ticker)`
   - si hay datos validos, los guarda con `db.actualizar_precio(datos)`
7. Espera el intervalo configurado antes de repetir.

## Comportamiento de parada

El script captura `KeyboardInterrupt`, por lo que puede detenerse manualmente desde consola sin mostrar un traceback.

## Ejecucion

Se ejecuta directamente cuando el archivo se lanza como script:

```python
if __name__ == "__main__":
    ejecutar_worker()
```

## Consideraciones

- El proceso esta pensado para ejecutarse continuamente en segundo plano.
- Si falta alguna variable de entorno o las credenciales son invalidas, el worker no podra inicializar correctamente sus servicios.
- El worker no guarda historico de precios; solo actualiza el estado actual en Firestore.
- El intervalo esta fijado en 60 segundos dentro del propio script.
