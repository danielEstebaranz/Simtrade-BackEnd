import finnhub

class ApiHandler:
    """
    Clase encargada de la comunicación con Finnhub.io.
    Su objetivo es centralizar las peticiones de mercado para no repetir código.
    """
    def __init__(self, api_key):
        # Inicializamos el cliente oficial de Finnhub con la API KEY
        self.client = finnhub.Client(api_key=api_key)

    def obtener_precio_actual(self, ticker):
        """
        Solicita el precio actual de un activo (ej: 'AAPL', 'BTC/USD').
        Retorna un diccionario limpio o None si hay error.
        """
        try:
            # Llamada al método 'quote' del SDK de Finnhub
            res = self.client.quote(ticker.upper())
            
            # Si el precio 'c' (current) es 0, es probable que el ticker no exista
            if res['c'] == 0:
                print(f" El activo {ticker} no devolvió datos válidos.")
                return None
            
            # Mapeamos las claves cortas de la API a nombres legibles
            return {
                "simbolo": ticker.upper(),
                "precio": res['c'],      # Precio actual
                "variacion": res['d'],   # Cambio en dólares
                "porcentaje": res['dp'], # Cambio en %
                "maximo": res['h'],      # Máximo del día
                "minimo": res['l']       # Mínimo del día
            }
        except Exception as e:
            print(f" Error de red en ApiHandler: {e}")
            return None