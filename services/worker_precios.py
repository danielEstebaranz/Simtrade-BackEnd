import os
import time
from dotenv import load_dotenv
from Api_Handler import ApiHandler
from db_handler import DbHandler
from market_assets import market_tickers

load_dotenv()

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
            time.sleep(INTERVALO)
    except KeyboardInterrupt:
        print("\n🛑 Worker detenido.")

if __name__ == "__main__":
    ejecutar_worker()
