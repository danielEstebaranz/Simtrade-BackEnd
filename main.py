import os
from dotenv import load_dotenv
from services.Api_Handler import ApiHandler
from services.db_handler import DbHandler

# Cargamos las variables del archivo .env al entorno de ejecución
load_dotenv()

def ejecutar_simulador():
    """
    Función principal comentada para el equipo.
    Lee las credenciales de forma segura desde el archivo .env
    """
    
    # 1. Recuperamos las variables de entorno
    # Usamos os.getenv para obtener los valores definidos en el .env
    api_key = os.getenv('FINNHUB_API_KEY')
    firebase_cert = os.getenv('FIREBASE_JSON_PATH')

    # 2. Inicialización de servicios
    # Pasamos las variables recuperadas a los Handlers
    finnhub_service = ApiHandler(api_key)
    firebase_service = DbHandler(firebase_cert)



    # 3. Flujo de trabajo
    ticker = 'TSLA'
    print(f"--- Iniciando proceso para {ticker} ---")
    
    datos = finnhub_service.obtener_precio_actual(ticker)

    if datos:
        print(f"Datos obtenidos correctamente para {ticker}")
        firebase_service.actualizar_precio(datos)
    else:
        print("Error: No se pudieron obtener datos de la API.")

if __name__ == "__main__":
    ejecutar_simulador()