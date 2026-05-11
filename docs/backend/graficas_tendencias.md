# Graficas de tendencias reales

## Objetivo

El backend proporciona datos historicos reales para que el frontend pueda pintar la grafica de una accion en la pestaña `Cartera`.

La ruta principal es:

```text
GET /market/{ticker}/trend?range={rango}
```

Ejemplos:

```text
GET http://127.0.0.1:8000/market/AAPL/trend?range=1d
GET http://127.0.0.1:8000/market/AAPL/trend?range=1w
GET http://127.0.0.1:8000/market/AAPL/trend?range=1y
```

## Por que se hizo en backend

La grafica podria parecer una cosa visual, pero el dato no debe inventarse en Angular.

El frontend debe encargarse de pintar. El backend debe encargarse de pedir datos reales.

Asi queda separado:

```text
Angular + Chart.js -> pintar grafica
FastAPI + ApiHandler + yfinance -> obtener datos reales
```

## Libreria usada

Se usa `yfinance`.

Motivos:

- permite pedir historicos con poco codigo
- no necesita manejar manualmente velas de mercado
- devuelve datos faciles de transformar
- sirve para tickers comunes como `AAPL`, `MSFT`, `TSLA`, etc.

## Flujo interno

```text
api_server.py
  -> recibe ticker y range
  -> valida que range sea 1d, 1w o 1y
  -> llama a market_api.obtener_tendencia(ticker, rango)

Api_Handler.py
  -> normaliza ticker
  -> pide historico con yfinance
  -> toma columna Close
  -> convierte fechas a timestamp
  -> compacta puntos si hay demasiados
  -> devuelve JSON al frontend
```

## Respuesta

```json
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

## Por que se usa `Close`

`Close` es el precio de cierre de cada intervalo.

Para una grafica de tendencia sencilla es suficiente y evita mezclar muchos datos como apertura, maximo, minimo y volumen.

## Compactacion de puntos

El metodo `_compactar_puntos(...)` limita la cantidad de puntos enviados.

Motivo:

- una grafica no necesita cientos o miles de puntos para verse bien
- enviar menos datos hace mas ligera la respuesta
- Chart.js actualiza mas rapido

## Errores posibles

### Rango invalido

Si llega un rango que no sea `1d`, `1w` o `1y`, el backend devuelve `400`.

### Ticker sin historico

Si yfinance no devuelve datos, el backend devuelve `404`.

### Backend no arrancado

Si FastAPI no esta arrancado en `127.0.0.1:8000`, Angular no puede cargar la grafica.

### Proceso antiguo en el puerto

Puede ocurrir que el puerto `8000` este ocupado por un backend anterior. En ese caso parece que los cambios no funcionan aunque el codigo sea correcto.

Solucion:

```powershell
netstat -ano | Select-String ":8000"
Stop-Process -Id <PID> -Force
python api_server.py
```

## Prueba manual

```powershell
curl.exe -s -i "http://127.0.0.1:8000/market/AAPL/trend?range=1d"
```

Respuesta correcta esperada:

```text
HTTP/1.1 200 OK
```

Y en el JSON:

```json
"source": "yfinance"
```

## Puntos debiles

- Depende de que yfinance pueda acceder a datos externos.
- Algunos tickers pueden necesitar formato especial.
- No hay cache de historicos.
- No se guardan historicos en Firestore.
- No hay control de rate limit avanzado.

## Mejoras futuras

- Crear cache temporal por ticker y rango.
- Anadir endpoint de busqueda de tickers.
- Guardar el ultimo historico consultado si se quiere trabajar sin conexion.
- Usar una libreria de autenticacion real para proteger endpoints privados.
