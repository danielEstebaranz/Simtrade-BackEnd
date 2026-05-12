# Ganancias de cartera

## Objetivo

El backend calcula las ganancias que se muestran en la pestaña `Cartera` del frontend:

- ganancias totales
- ganancias diarias

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

## Puntos debiles

- El fallback asume saldo inicial de 1000 $.
- Si el usuario recibe ingresos extra o cambios manuales de saldo, la estimacion puede ser inexacta.
- Lo ideal a futuro seria guardar precio medio o coste abierto por activo en Firestore.
- No hay cache de precios, por lo que se consulta yfinance para calcular valores actuales.
