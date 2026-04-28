import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

class DbHandler:
    def __init__(self, certificado_path):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(certificado_path)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("🔥 Conexión establecida con Firebase Firestore.")
        except Exception as e:
            print(f"❌ Error crítico al conectar con Firebase: {e}")

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
            print(f"❌ Error al actualizar precio: {e}")

    def obtener_usuario(self, user_id="usuario_demo"):
        user_ref = self.db.collection('usuarios').document(user_id)
        doc = user_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            datos_iniciales = {'saldo': 1000.0, 'cartera': {}}
            user_ref.set(datos_iniciales)
            return datos_iniciales

    # --- NUEVA FUNCIÓN INTERNA PARA EL HISTORIAL ---
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
            print(f"📝 Movimiento registrado: {tipo} de {ticker}")
        except Exception as e:
            print(f"❌ Error al escribir en historial: {e}")

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
                        .order_by('fecha', direction=firestore.Query.DESCENDING)\
                        .limit(20).get()
            return docs
        except Exception as e:
            print(f"❌ Error al consultar historial: {e}")
            return []