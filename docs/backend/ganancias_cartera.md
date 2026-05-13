# Ganancias de cartera

## Objetivo

El backend calcula las ganancias que se muestran en la pestaña `Cartera` del frontend:

- ganancias totales
- ganancias diarias
- valor actual por cada posicion

El endpoint es:

```text
GET /users/me/portfolio/gains
```

Requiere autenticacion:

```text
Authorization: Bearer <idToken>
```

## Respuesta

```json
{
  "costBasisSource": "history",
  "dailyGain": -0.06,
  "hasCostBasis": true,
  "investedCost": 10.0,
  "positions": {
    "BINANCE:BTCUSDT": {
      "costBasisSource": "history",
      "dailyGain": -0.83,
      "hasCostBasis": true,
      "investedCost": 49.32,
      "totalGain": -0.26,
      "totalValue": 49.06
    }
  },
  "source": "yfinance",
  "totalGain": 0.02,
  "totalValue": 10.02
}
```

## Campos

### `totalGain`

Ganancia o perdida total desde la compra:

```text
totalGain = totalValue - investedCost
```

### `dailyGain`

Ganancia o perdida del dia:

```text
dailyGain = cantidad * (ultimo precio del dia - primer precio del dia)
```

### `investedCost`

Dinero invertido usado para calcular la ganancia total.

### `totalValue`

Valor actual de todos los activos de la cartera.

### `positions`

Diccionario por ticker con los calculos de cada activo.

El frontend usa:

```text
positions[ticker].totalValue
```

para mostrar `Valor actual` en la tendencia de cartera.

### `hasCostBasis`

Indica si el backend pudo obtener o estimar un coste de inversion.

### `costBasisSource`

Indica de donde sale el coste:

```text
history          -> historial real de compras y ventas
balance_estimate -> estimacion con saldo inicial menos saldo actual
none             -> no calculable
```

## Prioridad de calculo

El backend intenta calcular el coste asi:

1. Lee el historial de transacciones del usuario.
2. Calcula el coste abierto de cada activo.
3. Si hubo ventas, resta el coste proporcional vendido.
4. Si no hay historial valido, estima:

```text
coste estimado = 1000 - saldo actual
```

La estimacion es un fallback. El dato preferente siempre es el historial real.

## Valor actual por posicion

Para cada activo se calcula:

```text
valor actual del activo = cantidad * ultimo precio real
```

Ese valor se devuelve en:

```text
positions[ticker].totalValue
```

No debe confundirse con `investedCost`:

- `investedCost`: dinero que costo abrir la posicion.
- `totalValue`: dinero que vale ahora mismo esa posicion.

En la UI se muestra `Valor actual` porque la zona de cartera permite vender y ese dato ayuda a estimar cuanto se recibira.

## Reparto de estimacion cuando no hay historial

Si no hay historial real, el backend estima:

```text
coste estimado total = 1000 - saldo actual
```

Despues reparte ese coste estimado entre posiciones segun el peso de cada una:

```text
peso posicion = valor actual posicion / valor actual total
coste estimado posicion = coste estimado total * peso posicion
```

Esto evita que las posiciones individuales aparezcan siempre como `Sin coste` cuando no hay transacciones antiguas disponibles.

## Por que puede haber total positivo y diario negativo

No es contradictorio.

La ganancia total compara contra la compra:

```text
Compraste por: 10,00 $
Ahora vale:    10,02 $
Total:         +0,02 $
```

La diaria compara contra el inicio del dia:

```text
Inicio del dia: 10,08 $
Ahora vale:     10,02 $
Diaria:         -0,06 $
```

La cartera puede seguir en positivo desde la compra aunque hoy haya bajado.

## Errores corregidos

### `Sin coste`

El frontend mostraba `Sin coste` porque el backend no encontraba historial de compras.

Se corrigio:

- leyendo transacciones por usuario
- ordenandolas en Python
- calculando coste abierto
- usando fallback con `1000 - saldo actual`

### Consulta ordenada por Firestore

La query anterior ordenaba por `fecha` directamente en Firestore. Eso puede requerir indice y fallar segun la estructura.

Ahora se consulta por usuario y se ordena en Python.

### `Dinero invertido` no era el mejor dato antes de vender

El frontend primero mostro `Dinero invertido` dentro de la tendencia.

Se cambio a `Valor actual` porque para vender por porcentaje interesa ver cuanto vale la posicion en el mercado en ese momento.

### Venta del 25 % no coincidia exactamente con el valor visible

El valor de la pantalla y el valor de venta pueden calcularse con precios consultados en momentos distintos.

La venta siempre usa el precio real consultado por el backend justo antes de ejecutar `realizar_venta`.

## Puntos debiles

- El fallback asume saldo inicial de 1000 $.
- Si el usuario recibe ingresos extra o cambios manuales de saldo, la estimacion puede ser inexacta.
- Lo ideal a futuro seria guardar precio medio o coste abierto por activo en Firestore.
- No hay cache de precios, por lo que se consulta yfinance para calcular valores actuales.
- La venta y la visualizacion pueden diferir unos centimos por fluctuacion de precio entre peticiones.
