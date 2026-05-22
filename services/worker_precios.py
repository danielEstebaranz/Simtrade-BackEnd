import os
import time
from dotenv import load_dotenv
from Api_Handler import ApiHandler
from db_handler import DbHandler
from market_assets import market_tickers

load_dotenv()

SIMULATED_DIVIDEND_DAYS_PER_CYCLE = 30
SIMULATED_ANNUAL_DIVIDEND_RATES = {
    'AAPL': 0.06,
    'AMZN': 0.02,
    'GOOGL': 0.03,
    'HINKF': 0.04,
    'MSFT': 0.05,
    'NVDA': 0.01,
    'NVD': 0.01,
    'TSLA': 0.0,
    'BINANCE:BTCUSDT': 0.0,
}


def reinvertir_dividendos_usuarios(api, db):
    reinversiones = 0

    for usuario in db.obtener_usuarios_con_cartera():
        user_id = usuario['id']
        cartera = usuario.get('cartera', {})

        for ticker, cantidad in cartera.items():
            cantidad = float(cantidad or 0)
            tasa_anual = SIMULATED_ANNUAL_DIVIDEND_RATES.get(str(ticker).upper(), 0.0)

            if cantidad <= 0 or tasa_anual <= 0:
                continue

            tendencia = api.obtener_tendencia(ticker, '1d')
            puntos = tendencia.get('points', []) if tendencia else []

            if not puntos:
                continue

            precio_actual = float(puntos[-1].get('price', 0) or 0)

            if precio_actual <= 0:
                continue

            valor_actual = cantidad * precio_actual
            importe_dividendo = round(
                valor_actual * tasa_anual * (SIMULATED_DIVIDEND_DAYS_PER_CYCLE / 365),
                2,
            )

            if importe_dividendo <= 0:
                continue

            ok, _ = db.reinvertir_dividendo(user_id, ticker, importe_dividendo, precio_actual)

            if ok:
                reinversiones += 1

    return reinversiones


def ejecutar_worker():
    api = ApiHandler(os.getenv('FINNHUB_API_KEY'))
    db = DbHandler(os.getenv('FIREBASE_JSON_PATH'))
    
    activos = market_tickers()
    INTERVALO = 60 # 1 minuto

    # Solo imprimimos esto al arrancar
    print(f"⚙️ Worker iniciado: Actualizando {len(activos)} activos cada minuto...")

    try:
        while True:
            for ticker in activos:
                datos = api.obtener_precio_actual(ticker)
                if datos:
                    db.actualizar_precio(datos)
                # Aquí no hay prints si todo va bien: silencio total.
            reinversiones = reinvertir_dividendos_usuarios(api, db)
            if reinversiones:
                print(f"Dividendos reinvertidos automaticamente: {reinversiones}")
            time.sleep(INTERVALO)
    except KeyboardInterrupt:
        print("\n🛑 Worker detenido.")

if __name__ == "__main__":
    ejecutar_worker()
