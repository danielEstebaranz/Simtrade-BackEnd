import firebase_admin
from firebase_admin import credentials, firestore

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

    def realizar_compra(self, ticker, cantidad, precio_unidad, user_id="usuario_demo"):
        user_ref = self.db.collection('usuarios').document(user_id)
        user_data = self.obtener_usuario(user_id)
        coste_total = cantidad * precio_unidad
        
        if user_data['saldo'] >= coste_total:
            nuevo_saldo = user_data['saldo'] - coste_total
            cartera = user_data.get('cartera', {})
            cartera[ticker] = cartera.get(ticker, 0) + cantidad
            user_ref.update({'saldo': nuevo_saldo, 'cartera': cartera})
            return True, nuevo_saldo
        return False, user_data['saldo']
    
    def realizar_venta(self, ticker, cantidad_a_vender, precio_unidad, user_id="usuario_demo"):
            user_ref = self.db.collection('usuarios').document(user_id)
            user_data = self.obtener_usuario(user_id)
            cartera = user_data.get('cartera', {})
            
            cantidad_actual = cartera.get(ticker, 0)
            
            # Validación de seguridad
            if cantidad_actual >= cantidad_a_vender:
                ingreso = cantidad_a_vender * precio_unidad
                nuevo_saldo = user_data['saldo'] + ingreso
                
                nueva_cantidad = cantidad_actual - cantidad_a_vender
                
                # Si la cantidad restante es insignificante, eliminamos el activo
                if nueva_cantidad < 0.000001:
                    if ticker in cartera:
                        del cartera[ticker]
                else:
                    cartera[ticker] = nueva_cantidad
                    
                user_ref.update({
                    'saldo': nuevo_saldo,
                    'cartera': cartera
                })
                return True, nuevo_saldo
            return False, user_data['saldo']