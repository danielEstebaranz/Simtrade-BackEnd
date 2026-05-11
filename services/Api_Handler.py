import math
import yfinance as yf

try:
    import finnhub
except ImportError:
    finnhub = None

class ApiHandler:
    """
    Clase encargada de la comunicación con Finnhub.io.
    Su objetivo es centralizar las peticiones de mercado para no repetir código.
    """
    def __init__(self, api_key=None):
        # Finnhub se conserva para precio actual; yfinance se usa para historicos.
        self.client = finnhub.Client(api_key=api_key) if api_key and finnhub is not None else None

    def obtener_precio_actual(self, ticker):
        """
        Solicita el precio actual de un activo (ej: 'AAPL', 'BTC/USD').
        Retorna un diccionario limpio o None si hay error.
        """
        if self.client is None:
            print(" FINNHUB_API_KEY no esta configurada.")
            return None

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

    def obtener_tendencia(self, ticker, rango):
        """Obtiene puntos historicos de precio para pintar una grafica."""
        configuracion = {
            '1d': {'period': '1d', 'interval': '5m'},
            '1w': {'period': '5d', 'interval': '30m'},
            '1y': {'period': '1y', 'interval': '1d'},
        }
        opciones = configuracion.get(rango)

        if opciones is None:
            return None

        try:
            simbolo = self._normalizar_simbolo_historico(ticker)
            historico = yf.Ticker(simbolo).history(
                period=opciones['period'],
                interval=opciones['interval'],
                auto_adjust=False,
            )

            if historico.empty or 'Close' not in historico:
                return None

            puntos = []
            cierres = historico['Close'].dropna()

            for fecha, precio in cierres.items():
                puntos.append({
                    'timestamp': int(fecha.timestamp()),
                    'price': float(precio),
                })

            if not puntos:
                return None

            return {
                'ticker': simbolo,
                'range': rango,
                'points': self._compactar_puntos(puntos),
                'source': 'yfinance',
            }
        except Exception as e:
            print(f" Error al obtener tendencia de {ticker}: {e}")
            return None

    def _normalizar_simbolo_historico(self, ticker):
        """Convierte algunos simbolos comunes al formato que espera Yahoo Finance."""
        simbolo = ticker.strip().upper()

        if simbolo == 'BINANCE:BTCUSDT':
            return 'BTC-USD'

        if simbolo.startswith('BINANCE:') and simbolo.endswith('USDT'):
            moneda = simbolo.replace('BINANCE:', '').replace('USDT', '')
            return f'{moneda}-USD'

        return simbolo

    def _compactar_puntos(self, puntos, max_puntos=80):
        """Reduce listas largas para que el frontend pinte una grafica ligera."""
        if len(puntos) <= max_puntos:
            return puntos

        salto = math.ceil(len(puntos) / max_puntos)
        compactados = puntos[::salto]

        if compactados[-1] != puntos[-1]:
            compactados.append(puntos[-1])

        return compactados
