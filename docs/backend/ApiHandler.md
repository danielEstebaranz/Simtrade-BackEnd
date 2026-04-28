# ApiHandler

Archivo fuente: [services/Api_Handler.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/Api_Handler.py)

## Proposito

`ApiHandler` encapsula la comunicacion con la API de Finnhub. Su responsabilidad es obtener cotizaciones de mercado y devolverlas en un formato interno mas legible para el resto del proyecto.

## Dependencias

- Libreria externa: `finnhub`
- Credencial necesaria: `FINNHUB_API_KEY`

## Constructor

### `__init__(api_key)`

Inicializa el cliente oficial de Finnhub usando la API key recibida.

### Parametros

- `api_key`: clave de acceso a Finnhub.

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

## Flujo interno

1. Llama a `self.client.quote(ticker.upper())`.
2. Comprueba si el campo `c` viene a `0`.
3. Si el dato es valido, mapea las claves cortas de Finnhub a nombres mas expresivos.
4. Si hay una excepcion, la captura y devuelve `None`.

## Uso dentro del proyecto

- [services/worker_precios.py](C:/Users/monsu/OneDrive/Documentos/GitHub/Simtrade-BackEnd/services/worker_precios.py): obtiene precios periodicamente para almacenarlos en Firestore.

## Consideraciones

- Si `api_key` es `None` o invalida, las llamadas a Finnhub fallaran.
- El metodo considera que un precio actual igual a `0` implica dato no valido.
- Los errores se informan por consola, pero no se relanzan.
