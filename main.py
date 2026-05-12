import os
from dotenv import load_dotenv
from firebase_admin import auth as firebase_auth
import requests
from services.db_handler import DbHandler

load_dotenv()

FIREBASE_WEB_API_KEY = os.getenv('FIREBASE_WEB_API_KEY', 'AIzaSyDRpzs5pDFYZlbERSIXPuijs8lF18khL-s')

def resolver_email(email_o_usuario):
    valor = email_o_usuario.strip().lower()
    if '@' in valor:
        return valor
    return ''

def resolver_nombre_visible(email_o_usuario):
    valor = email_o_usuario.strip()
    if '@' in valor:
        return valor.split('@', 1)[0]
    return valor

def iniciar_sesion_firebase(email, password):
    response = requests.post(
        f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}',
        json={
            'email': email,
            'password': password,
            'returnSecureToken': True,
        },
        timeout=30,
    )

    if response.status_code == 200:
        return True, response.json().get('localId')

    try:
        error_code = response.json().get('error', {}).get('message', '')
    except ValueError:
        error_code = ''

    errores = {
        'EMAIL_NOT_FOUND': 'No existe una cuenta con ese email.',
        'INVALID_PASSWORD': 'La contrasena no es correcta.',
        'USER_DISABLED': 'La cuenta esta deshabilitada.',
        'INVALID_LOGIN_CREDENTIALS': 'Las credenciales no son correctas.',
    }
    return False, errores.get(error_code, 'No se pudo iniciar sesion con Firebase Authentication.')

def mostrar_menu_login():
    print("\n" + "="*40)
    print("           ACCESO A SIMTRADE")
    print("="*40)
    print(" 1. Iniciar sesion")
    print(" 2. Registrarse")
    print(" 3. Salir")
    return input("\nSeleccione una opcion: ")

def iniciar_sesion(db):
    username = input("Usuario: ").strip()
    password = input("Contrasena: ").strip()
    email = resolver_email(username)

    if not email:
        print("\nError: debes introducir un email valido.")
        return None

    ok, resultado = iniciar_sesion_firebase(email, password)
    if ok:
        print(f"\nBienvenido, {username}.")
        return resultado

    print(f"\nError: {resultado}")
    return None

def registrarse(db):
    username = input("Elige un nombre de usuario: ").strip()
    password = input("Elige una contrasena: ").strip()
    email = resolver_email(username)

    if not username or not password:
        print("\nError: usuario y contrasena son obligatorios.")
        return None

    if len(password) < 6:
        print("\nError: la contrasena debe tener al menos 6 caracteres.")
        return None

    if not email:
        print("\nError: para registrarte debes usar un email valido.")
        return None

    try:
        user_record = firebase_auth.create_user(
            email=email,
            password=password,
            display_name=resolver_nombre_visible(username),
        )
        db.crear_perfil_auth(user_record.uid, email, resolver_nombre_visible(username))
        print(f"\nUsuario {username} creado correctamente.")
        return user_record.uid
    except ValueError as exc:
        print(f"\nError: {exc}")
        return None
    except Exception as exc:
        print(f"\nError: no se pudo crear el usuario en Firebase Authentication: {exc}")
        return None


def autenticar_usuario(db):
    while True:
        opcion = mostrar_menu_login()

        if opcion == '1':
            user_id = iniciar_sesion(db)
            if user_id:
                return user_id
        elif opcion == '2':
            user_id = registrarse(db)
            if user_id:
                return user_id
        elif opcion == '3':
            return None
        else:
            print("\nOpcion no valida.")

def mostrar_menu(saldo):
    print(f"\n" + "="*40)
    print(f"  SIMTRADE | SALDO DISPONIBLE: {saldo:.2f}$")
    print("="*40)
    print(" 1.  Ver Mercado e Invertir")
    print(" 2.  Ver mi Cartera")
    print(" 3.  Consultar transacciones")
    print(" 4.  Cerrar sesion")
    print(" 5.  Salir")
    return input("\nSeleccione una opcion: ")

def app_usuario():
    db = DbHandler(os.getenv('FIREBASE_JSON_PATH'))
    mercado_tickers = ['AAPL', 'TSLA', 'AMZN', 'MSFT', 'BINANCE:BTCUSDT']

    while True:
        user_id = autenticar_usuario(db)

        if not user_id:
            print("\nSaliendo de Simtrade.")
            return

        user_data = db.obtener_usuario(user_id)

        while True:
            user_data = db.obtener_usuario(user_id)
            opcion = mostrar_menu(user_data['saldo'])

            if opcion == '1':
                print("\n--- PRECIOS EN TIEMPO REAL (via Firebase) ---")
                precios_locales = {}
                for i, ticker in enumerate(mercado_tickers):
                    # Leemos de nuestra BD, NO de la API externa
                    doc = db.db.collection('mercado').document(ticker).get()
                    if doc.exists:
                        precio = doc.to_dict().get('precio_actual')
                        precios_locales[i+1] = (ticker, precio)
                        print(f"{i+1}. {ticker}: {precio:.2f}$")
                
                try:
                    sel = int(input("\nNumero de accion para comprar (0 para volver): "))
                    if sel in precios_locales:
                        t_sel, p_sel = precios_locales[sel]
                        monto = float(input(f"Cuanto dinero ($) quieres invertir en {t_sel}?: "))
                        
                        cantidad = monto / p_sel
                        exito, nuevo_saldo = db.realizar_compra(t_sel, cantidad, p_sel, user_id)
                        
                        if exito:
                            print(f"\nExito. Has comprado {cantidad:.4f} unidades de {t_sel}.")
                        else:
                            print("\nError: Saldo insuficiente.")
                except Exception as e:
                    print(f"Error en la operacion: {e}")

            elif opcion == '2':
                print("\n" + "-"*30)
                print("       TU CARTERA ACTUAL")
                print("-"*30)
                cartera = user_data.get('cartera', {})
                
                if not cartera:
                    print("No tienes activos todavia.")
                else:
                    opciones_venta = {}
                    for i, (ticker, cant) in enumerate(cartera.items()):
                        doc = db.db.collection('mercado').document(ticker).get()
                        p_act = doc.to_dict().get('precio_actual', 0) if doc.exists else 0
                        opciones_venta[i+1] = (ticker, cant, p_act)
                        print(f"{i+1}. {ticker:8} | Cant.: {cant:.4f} | Valor Actual: {cant*p_act:.2f}$")
                    
                    print("\n0. Volver")
                    try:
                        sel = int(input("\nSeleccione el numero de accion para gestionar venta: "))
                        if sel in opciones_venta:
                            t_sel, c_max, p_sel = opciones_venta[sel]
                            
                            print(f"\nGestion de {t_sel} (Max: {c_max:.4f} unidades)")
                            print(f"1. Vender 25% ({(c_max*0.25):.4f} ud)")
                            print(f"2. Vender 50% ({(c_max*0.50):.4f} ud)")
                            print(f"3. Vender 100% ({c_max:.4f} ud)")
                            print("4. Introducir cantidad manual")
                            
                            sub_opc = input("Seleccione opcion de venta: ")
                            
                            c_vender = 0
                            if sub_opc == '1':
                                c_vender = c_max * 0.25
                            elif sub_opc == '2':
                                c_vender = c_max * 0.50
                            elif sub_opc == '3':
                                c_vender = c_max
                            elif sub_opc == '4':
                                c_vender = float(input(f"Cuantas unidades quieres vender? (Max {c_max:.4f}): "))
                            
                            if c_vender > 0:
                                exito, s_final = db.realizar_venta(t_sel, c_vender, p_sel, user_id)
                                if exito:
                                    print(f"\nVenta completada. Has recibido {(c_vender*p_sel):.2f}$.")
                                    print(f"Nuevo saldo total: {s_final:.2f}$")
                                else:
                                    print("Error en la venta.")
                    except ValueError:
                        print("Entrada no valida.")
            elif opcion == '3':
                print("\n" + "="*50)
                print("         MI HISTORIAL DE OPERACIONES")
                print("="*50)
                
                movimientos = db.obtener_historial(user_id)
                
                if not movimientos:
                    print("No hay movimientos registrados en tu cuenta.")
                else:
                    for doc in movimientos:
                        t = doc.to_dict()
                        fecha = t['fecha'].strftime("%d/%m/%Y %H:%M") if t['fecha'] else "Pendiente..."
                        print(f"[{fecha}] {t['tipo']:7} | {t['ticker']:8} | Cant: {t['cantidad']:.4f} | Total: {t['total_dinero']:.2f}$")
                
                input("\nPresiona Enter para volver...")
            elif opcion == '4':
                print("\nSesion cerrada.")
                break
            elif opcion == '5':
                print("\nSaliendo de Simtrade.")
                return
            else:
                print("\nOpcion no valida.")

if __name__ == "__main__":
    app_usuario()
