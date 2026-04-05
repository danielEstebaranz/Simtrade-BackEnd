import firebase_admin
from firebase_admin import credentials, firestore

class DbHandler:
    """
    Clase para gestionar la persistencia de datos en Firebase Firestore.
    Permite que el simulador guarde precios en la nube en tiempo real.
    """
    def __init__(self, certificado_path):
        """
        Configura la conexión inicial con el SDK de Firebase.
        """
        try:
            # Verificamos si Firebase ya ha sido inicializado para evitar errores
            if not firebase_admin._apps:
                # Cargamos el certificado JSON descargado de la consola de Firebase
                cred = credentials.Certificate(certificado_path)
                firebase_admin.initialize_app(cred)
            
            # Creamos el cliente de Firestore
            self.db = firestore.client()
            print(" Conexión establecida con Firebase Firestore.")
        except Exception as e:
            print(f" Error crítico al conectar con Firebase: {e}")

    def actualizar_precio(self, datos):
        """
        Recibe el diccionario de la API y lo sube a la colección 'mercado'.
        Si el documento ya existe, sobrescribe los valores (Update).
        """
        if not datos:
            return

        try:
            # Definimos la ubicación: Colección 'mercado' / Documento 'NOMBRE_TICKER'
            doc_ref = self.db.collection('mercado').document(datos['simbolo'])
            
            # Enviamos los datos a la nube
            doc_ref.set({
                'precio_actual': datos['precio'],
                'cambio_diario': datos['variacion'],
                'porcentaje': datos['porcentaje'],
                'max_dia': datos['maximo'],
                'min_dia': datos['minimo'],
                # SERVER_TIMESTAMP asegura que la hora sea la de Google, no la local
                'ultima_sincronizacion': firestore.SERVER_TIMESTAMP 
            })
            print(f" Firebase: {datos['simbolo']} actualizado con éxito.")
        except Exception as e:
            print(f" Error al intentar subir datos a Firestore: {e}")