# worker_precios

Archivo fuente: [services/worker_precios.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/worker_precios.py)

## Proposito

`worker_precios.py` es un script de backend encargado de sincronizar precios de mercado desde Finnhub hacia Firebase Firestore de forma periodica y de aplicar la reinversion automatica de dividendos simulados.

## Responsabilidad dentro del sistema

Este worker mantiene actualizada la coleccion `mercado` en Firestore para que la aplicacion principal pueda consultar precios desde la base de datos sin llamar directamente a la API externa en cada operacion del usuario.

Tambien revisa las carteras de los usuarios y, cuando un activo tiene una tasa simulada de dividendo, convierte ese importe en mas unidades del mismo activo. El saldo disponible no cambia.

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
4. Carga la lista comun de activos desde `services/market_assets.py`:
   - `AAPL`
   - `TSLA`
   - `AMZN`
   - `MSFT`
   - `BINANCE:BTCUSDT`
   - `GOOGL`
   - `NVD`
5. Define un intervalo de 60 segundos.
6. En cada iteracion:
   - consulta el precio de cada activo con `api.obtener_precio_actual(ticker)`
   - si hay datos validos, los guarda con `db.actualizar_precio(datos)`
   - revisa usuarios con cartera
   - calcula dividendos simulados sobre el valor actual de cada posicion
   - reinvierte el importe comprando fracciones del mismo activo
7. Espera el intervalo configurado antes de repetir.

## Reinversion automatica de dividendos

La reinversion se hace en la funcion:

```python
reinvertir_dividendos_usuarios(api, db)
```

El calculo usa una simulacion sencilla:

```text
dividendo = valor actual * tasa anual simulada * dias simulados / 365
```

Actualmente cada ciclo simula 30 dias para que el efecto pueda verse durante las pruebas del proyecto.

La tabla de tasas esta definida en el propio worker:

```python
DIVIDEND_RATES = {
    'AAPL': 0.06,
    'AMZN': 0.02,
    'GOOGL': 0.03,
    'MSFT': 0.05,
    'TSLA': 0.0,
    'BINANCE:BTCUSDT': 0.0,
}
```

Es decir, las tasas estan hardcodeadas porque son una simulacion del proyecto. La reinversion no se aplica a toda esa tabla, sino solo a los activos que cada usuario tenga realmente en `cartera`.

El flujo exacto es:

```text
usuario tiene cartera
  -> se recorren sus tickers actuales
  -> se busca la tasa simulada de cada ticker
  -> si la tasa no existe o es 0, se ignora
  -> si tiene tasa mayor que 0, se calcula el dividendo de esa posicion
```

Por ejemplo, aunque `TSLA` exista en la tabla, tiene tasa `0.0`, asi que no genera reinversion. Si el usuario no tiene `TSLA` en cartera, ni siquiera se intenta calcular.

### Relacion entre tiempo real y tiempo simulado

El worker se ejecuta cada 60 segundos:

```python
INTERVALO = 60
```

Pero cada ciclo simula 30 dias de dividendo:

```python
DIVIDEND_DAYS_PER_CYCLE = 30
```

Por tanto, en esta demo:

```text
1 minuto real = 30 dias simulados de dividendo
```

No significa que 1 minuto sea 1 dia. Se acelero a 30 dias por ciclo para que la reinversion se pueda observar durante una presentacion corta. Si se quisiera que 1 minuto representase 1 dia, bastaria con cambiar `DIVIDEND_DAYS_PER_CYCLE` a `1`, aunque el efecto seria mucho menos visible.

Ese importe no se suma al saldo. Se transforma directamente en mas unidades del mismo activo:

```text
unidades nuevas = dividendo / precio actual
```

La operacion se guarda como `DIVIDENDO_REINVERTIDO`. Queda en Firestore para que el calculo de coste invertido sea consistente, pero no se muestra en el historial visible del usuario.

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
- Este script no participa en el login, pero si actualiza carteras cuando aplica dividendos simulados.
- La reinversion es una simplificacion para el TFG: no consulta calendarios reales de dividendos ni fechas ex-dividend.

## Por que esta hecho asi

- Se ha separado del resto del backend porque actualizar precios continuamente y atender usuarios son responsabilidades distintas.
- Se usa un bucle simple con `time.sleep(60)` porque es suficiente para este proyecto y es mucho mas facil de entender que un sistema de colas o tareas programadas.
- Se escriben los precios en Firestore para que tanto la consola como el frontend lean una fuente comun ya procesada.
- Se reutiliza el worker para reinversion porque ya es el proceso periodico que corre en segundo plano.
- No se registra historico de precios porque el objetivo actual es mostrar el precio vigente para la simulacion, no construir una analitica temporal avanzada.
- La lista de tickers no se duplica aqui; se reutiliza `market_tickers()` para que API y worker compartan el mismo catalogo.
