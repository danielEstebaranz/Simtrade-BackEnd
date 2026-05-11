# ApiHandler

Archivo fuente: [services/Api_Handler.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/Api_Handler.py)

## Proposito

`ApiHandler` encapsula la comunicacion con proveedores de mercado. Actualmente conserva Finnhub para precio actual y usa yfinance para historicos reales de tendencia.

## Dependencias

- Libreria externa: `finnhub`
- Libreria externa: `yfinance`
- Credencial opcional: `FINNHUB_API_KEY`
- Servicio externo: Finnhub para precio actual
- Servicio externo: Yahoo Finance mediante yfinance para historicos

## Constructor

### `__init__(api_key=None)`

Inicializa el cliente oficial de Finnhub si hay API key y la libreria esta instalada. Si no, deja Finnhub desactivado pero permite seguir usando yfinance para historicos.

### Parametros

- `api_key`: clave de acceso a Finnhub. Es opcional para la grafica historica.

## Metodos

### `obtener_precio_actual(ticker)`

Solicita la cotizacion actual de un activo y transforma la respuesta de Finnhub a un diccionario propio del proyecto.

### Parametros

- `ticker`: simbolo del activo. El metodo lo convierte a mayusculas antes de consultar.

### Retorno

Devuelve un diccionario con esta estructura cuando la consulta es valida:

```python
{
    "simbolo": "TSLA",
    "precio": 0.0,
    "variacion": 0.0,
    "porcentaje": 0.0,
    "maximo": 0.0,
    "minimo": 0.0
}
```

Si la API no devuelve datos utiles o ocurre un error, retorna `None`.

Si Finnhub no esta instalado o no hay API key, tambien retorna `None`.

### `obtener_tendencia(ticker, rango)`

Obtiene puntos historicos reales de precio para que el frontend pinte una grafica.

### Parametros

- `ticker`: simbolo del activo, por ejemplo `AAPL`.
- `rango`: rango temporal. Valores permitidos:
  - `1d`
  - `1w`
  - `1y`

### Retorno

Devuelve:

```python
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

Si no hay datos reales o ocurre un error, devuelve `None`.

### `_normalizar_simbolo_historico(ticker)`

Convierte algunos simbolos al formato que espera Yahoo Finance.

Ejemplo:

```text
BINANCE:BTCUSDT -> BTC-USD
```

### `_compactar_puntos(puntos, max_puntos=80)`

Reduce listas muy largas de puntos para que el frontend pinte la grafica de forma ligera.

No cambia el significado de la tendencia, solo evita enviar demasiados puntos cuando no hace falta.

## Flujo interno

1. Llama a `self.client.quote(ticker.upper())`.
2. Comprueba si el campo `c` viene a `0`.
3. Si el dato es valido, mapea las claves cortas de Finnhub a nombres mas expresivos.
4. Si hay una excepcion, la captura y devuelve `None`.

## Flujo interno de historico

1. Normaliza el ticker.
2. Selecciona periodo e intervalo segun `1d`, `1w` o `1y`.
3. Llama a `yf.Ticker(simbolo).history(...)`.
4. Extrae la columna `Close`.
5. Convierte cada fecha a timestamp Unix.
6. Devuelve una lista compactada de puntos.

## Uso dentro del proyecto

- [services/worker_precios.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/worker_precios.py): obtiene precios periodicamente para almacenarlos en Firestore.
- [api_server.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/api_server.py): obtiene tendencias reales para el frontend.

## Activos usados actualmente

El backend consulta actualmente estos tickers:

- `AAPL`
- `TSLA`
- `AMZN`
- `MSFT`
- `BINANCE:BTCUSDT`

## Consideraciones

- Si `api_key` es `None` o invalida, las llamadas a Finnhub no devolveran precio actual.
- La grafica historica no depende de Finnhub; usa yfinance.
- El metodo considera que un precio actual igual a `0` implica dato no valido.
- Los errores se informan por consola, pero no se relanzan.
- Esta clase solo lee datos del mercado; no interactua con usuarios ni con Firestore.
- Si Yahoo Finance no reconoce un ticker, `obtener_tendencia` devuelve `None`.

## Por que esta hecho asi

- Se usa una clase separada para Finnhub en lugar de llamadas directas desde otros archivos para evitar repetir codigo de acceso a mercado.
- Se devuelve un diccionario simple con nombres propios del proyecto porque es mas facil de entender que trabajar con las claves cortas originales de Finnhub.
- Se captura la excepcion y se devuelve `None` en vez de romper la ejecucion completa porque el worker puede seguir funcionando en la siguiente iteracion.
- Se usa yfinance para historicos porque simplifica la grafica real sin montar una integracion de velas a mano.
- Se dejo Finnhub como import opcional para que no bloquee el backend si solo se necesita la grafica historica.
