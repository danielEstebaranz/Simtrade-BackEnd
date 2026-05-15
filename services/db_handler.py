import firebase_admin
import hashlib
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter


DEFAULT_SETTINGS = {
    'theme': 'light',
}


class DbHandler:
    def __init__(self, certificado_path):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(certificado_path)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("Conexión establecida con Firebase Firestore.")
        except Exception as e:
            print(f"Error crítico al conectar con Firebase: {e}")
    
    def actualizar_precio(self, datos):
        """Actualiza los precios en la colección 'mercado'"""
        try:
            doc_ref = self.db.collection('mercado').document(datos['simbolo'])
            doc_ref.set({
                'precio_actual': datos['precio'],
                'cambio': datos['variacion'],
                'porcentaje': datos['porcentaje'],
                'ultima_actualizacion': firestore.SERVER_TIMESTAMP 
            })
        except Exception as e:
            print(f"Error al actualizar precio: {e}")

    def _encriptar_password(self, password):
        """Genera un hash simple de la contraseña para no guardar texto plano."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def crear_usuario(self, username, password):
        """Crea un usuario nuevo en Firestore si no existe."""
        user_id = username.strip().lower()
        user_ref = self.db.collection('usuarios').document(user_id)
        doc = user_ref.get()

        if doc.exists:
            return False, "Ese usuario ya existe."

        datos_usuario = {
            'username': username.strip(),
            'password': self._encriptar_password(password),
            'saldo': 1000.0,
            'cartera': {},
            'settings': DEFAULT_SETTINGS.copy(),
            'fecha_creacion': firestore.SERVER_TIMESTAMP
        }
        user_ref.set(datos_usuario)
        return True, user_id

    def crear_perfil_auth(self, uid, email, username):
        """Crea o actualiza el perfil de un usuario autenticado con Firebase Auth."""
        user_ref = self.db.collection('usuarios').document(uid)
        doc = user_ref.get()
        datos_perfil = {
            'username': username.strip(),
            'email': email.strip().lower(),
            'auth_provider': 'firebase_auth',
        }

        if doc.exists:
            user_ref.set(datos_perfil, merge=True)
        else:
            user_ref.set({
                **datos_perfil,
                'saldo': 1000.0,
                'cartera': {},
                'settings': DEFAULT_SETTINGS.copy(),
                'fecha_creacion': firestore.SERVER_TIMESTAMP,
            })

        return self.obtener_usuario(uid)

    def autenticar_usuario(self, username, password):
        """Valida usuario y contraseña contra Firestore."""
        user_id = username.strip().lower()
        user_ref = self.db.collection('usuarios').document(user_id)
        doc = user_ref.get()

        if not doc.exists:
            return False, "El usuario no existe."

        user_data = doc.to_dict()
        password_guardada = user_data.get('password')
        password_recibida = self._encriptar_password(password)

        if password_guardada != password_recibida:
            return False, "La contraseña no es correcta."

        return True, user_id

    def obtener_usuario(self, user_id="usuario_demo"):
        user_ref = self.db.collection('usuarios').document(user_id)
        doc = user_ref.get()
        if doc.exists:
            datos_usuario = doc.to_dict()
            if 'saldo' not in datos_usuario:
                datos_usuario['saldo'] = 1000.0
            if 'cartera' not in datos_usuario:
                datos_usuario['cartera'] = {}
            datos_usuario['settings'] = self._normalizar_settings(datos_usuario)
            return datos_usuario
        else:
            datos_iniciales = {
                'username': user_id,
                'password': '',
                'saldo': 1000.0,
                'cartera': {},
                'settings': DEFAULT_SETTINGS.copy(),
            }
            user_ref.set(datos_iniciales)
            return datos_iniciales

    def _normalizar_settings(self, user_data):
        """Devuelve la configuracion publica con valores seguros por defecto."""
        settings = user_data.get('settings') or {}
        theme = str(settings.get('theme', DEFAULT_SETTINGS['theme'])).strip().lower()

        if theme not in {'dark', 'light'}:
            theme = DEFAULT_SETTINGS['theme']

        return {
            'theme': theme,
        }

    def obtener_cartera(self, user_id):
        """Devuelve la cartera del usuario como lista simple de posiciones."""
        user_data = self.obtener_usuario(user_id)
        cartera = user_data.get('cartera', {})

        return [
            {
                'ticker': ticker,
                'cantidad': cantidad,
            }
            for ticker, cantidad in cartera.items()
        ]

    def obtener_perfil_publico(self, user_id):
        """Devuelve un perfil seguro para la API, sin datos sensibles."""
        user_data = self.obtener_usuario(user_id)
        return {
            'id': user_id,
            'username': user_data.get('username', user_id),
            'email': user_data.get('email', ''),
            'saldo': user_data.get('saldo', 1000.0),
            'cartera': user_data.get('cartera', {}),
            'settings': self._normalizar_settings(user_data),
        }

    def obtener_configuracion(self, user_id):
        """Lee las preferencias de configuracion del usuario."""
        user_data = self.obtener_usuario(user_id)
        return self._normalizar_settings(user_data)

    def actualizar_tema(self, user_id, theme):
        """Actualiza el modo visual elegido por el usuario."""
        user_ref = self.db.collection('usuarios').document(user_id)
        self.obtener_usuario(user_id)
        settings = {
            **DEFAULT_SETTINGS,
            'theme': theme,
        }
        user_ref.update({'settings': settings})
        return settings

    def _registrar_transaccion(self, user_id, tipo, ticker, cantidad, precio, total):
        """Guarda un registro de la operación en la colección 'transacciones'."""
        try:
            trans_ref = self.db.collection('transacciones').document()
            trans_ref.set({
                'usuario': user_id,
                'tipo': tipo,
                'ticker': ticker,
                'cantidad': cantidad,
                'precio_unidad': precio,
                'total_dinero': total,
                'fecha': firestore.SERVER_TIMESTAMP
            })
            print(f"Movimiento registrado: {tipo} de {ticker}")
        except Exception as e:
            print(f"Error al escribir en historial: {e}")

    def anadir_fondos(self, user_id, cantidad):
        """Suma fondos al saldo disponible del usuario y registra el movimiento."""
        user_ref = self.db.collection('usuarios').document(user_id)
        user_data = self.obtener_usuario(user_id)
        saldo_actual = float(user_data.get('saldo', 1000.0) or 0)
        nuevo_saldo = round(saldo_actual + cantidad, 2)
        user_ref.update({'saldo': nuevo_saldo})
        self._registrar_transaccion(user_id, 'DEPOSITO', 'CASH', 1, cantidad, cantidad)
        return nuevo_saldo

    def retirar_fondos(self, user_id, cantidad):
        """Resta fondos del saldo disponible del usuario y registra el movimiento."""
        user_ref = self.db.collection('usuarios').document(user_id)
        user_data = self.obtener_usuario(user_id)
        saldo_actual = float(user_data.get('saldo', 1000.0) or 0)

        if cantidad > saldo_actual:
            return False, saldo_actual

        nuevo_saldo = round(saldo_actual - cantidad, 2)
        user_ref.update({'saldo': nuevo_saldo})
        self._registrar_transaccion(user_id, 'RETIRADA', 'CASH', 1, cantidad, cantidad)
        return True, nuevo_saldo

    def reiniciar_cartera(self, user_id, saldo_inicial=1000.0):
        """Deja la cartera en el estado inicial y registra el reinicio."""
        user_ref = self.db.collection('usuarios').document(user_id)
        self.obtener_usuario(user_id)
        user_ref.update({
            'saldo': float(saldo_inicial),
            'cartera': {},
        })
        self._registrar_transaccion(user_id, 'REINICIO', 'CASH', 1, saldo_inicial, 0)
        return float(saldo_inicial)

    def eliminar_cuenta(self, user_id):
        """Borra el perfil de Firestore y sus transacciones asociadas."""
        transacciones = self.db.collection('transacciones')\
                            .where(filter=FieldFilter('usuario', '==', user_id))\
                            .get()
        batch = self.db.batch()
        operaciones_batch = 0
        transacciones_borradas = 0

        for transaccion in transacciones:
            batch.delete(transaccion.reference)
            operaciones_batch += 1
            transacciones_borradas += 1

            if operaciones_batch == 450:
                batch.commit()
                batch = self.db.batch()
                operaciones_batch = 0

        if operaciones_batch:
            batch.commit()

        self.db.collection('usuarios').document(user_id).delete()
        return {
            'deleted_transactions': transacciones_borradas,
        }

    def realizar_compra(self, ticker, cantidad, precio_unidad, user_id="usuario_demo"):
        user_ref = self.db.collection('usuarios').document(user_id)
        user_data = self.obtener_usuario(user_id)
        coste_total = cantidad * precio_unidad
        
        if user_data['saldo'] >= coste_total:
            nuevo_saldo = user_data['saldo'] - coste_total
            cartera = user_data.get('cartera', {})
            cartera[ticker] = cartera.get(ticker, 0) + cantidad
            user_ref.update({'saldo': nuevo_saldo, 'cartera': cartera})
            
            # LLAMADA AL HISTORIAL
            self._registrar_transaccion(user_id, 'COMPRA', ticker, cantidad, precio_unidad, coste_total)
            
            return True, nuevo_saldo
        return False, user_data['saldo']
    
    def realizar_venta(self, ticker, cantidad_a_vender, precio_unidad, user_id="usuario_demo"):
        user_ref = self.db.collection('usuarios').document(user_id)
        user_data = self.obtener_usuario(user_id)
        cartera = user_data.get('cartera', {})
        cantidad_actual = cartera.get(ticker, 0)
        
        if cantidad_actual >= cantidad_a_vender:
            ingreso = cantidad_a_vender * precio_unidad
            nuevo_saldo = user_data['saldo'] + ingreso
            nueva_cantidad = cantidad_actual - cantidad_a_vender
            
            if nueva_cantidad < 0.000001:
                if ticker in cartera: del cartera[ticker]
            else:
                cartera[ticker] = nueva_cantidad
                
            user_ref.update({'saldo': nuevo_saldo, 'cartera': cartera})
            
            # LLAMADA AL HISTORIAL
            self._registrar_transaccion(user_id, 'VENTA', ticker, cantidad_a_vender, precio_unidad, ingreso)
            
            return True, nuevo_saldo
        return False, user_data['saldo']

    def obtener_historial(self, user_id):
        try:
            docs = self.db.collection('transacciones')\
                        .where(filter=FieldFilter('usuario', '==', user_id))\
                        .get()
            transacciones = []

            for doc in docs:
                transaccion = doc.to_dict()
                transaccion['id'] = doc.id
                transacciones.append(transaccion)

            return sorted(
                transacciones,
                key=lambda transaccion: transaccion.get('fecha') or '',
                reverse=True,
            )[:20]
        except Exception as e:
            print(f"Error al consultar historial: {e}")
            return []

    def obtener_transacciones_usuario(self, user_id):
        """Devuelve todas las transacciones del usuario ordenadas de mas antigua a mas reciente."""
        try:
            docs = self.db.collection('transacciones')\
                        .where(filter=FieldFilter('usuario', '==', user_id)).get()
            transacciones = [doc.to_dict() for doc in docs]

            return sorted(
                transacciones,
                key=lambda transaccion: transaccion.get('fecha') or '',
            )
        except Exception as e:
            print(f"Error al consultar transacciones del usuario: {e}")
            return []
