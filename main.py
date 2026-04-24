import os
from dotenv import load_dotenv
from services.db_handler import DbHandler

load_dotenv()

def mostrar_menu(saldo):
    print(f"\n" + "="*40)
    print(f" 📈 SIMTRADE | SALDO DISPONIBLE: {saldo:.2f}$")
    print("="*40)
    print(" 1. 🔍 Ver Mercado e Invertir")
    print(" 2. 💼 Ver mi Cartera")
    print(" 3. 🚪 Salir")
    return input("\nSeleccione una opción: ")

def app_usuario():
    db = DbHandler(os.getenv('FIREBASE_JSON_PATH'))
    # El ID del activo se corresponde con el documento en la colección 'mercado'
    mercado_tickers = ['AAPL', 'TSLA', 'AMZN', 'MSFT', 'BINANCE:BTCUSDT']

    while True:
        user_data = db.obtener_usuario()
        opcion = mostrar_menu(user_data['saldo'])

        if opcion == '1':
            print("\n--- PRECIOS EN TIEMPO REAL (vía Firebase) ---")
            precios_locales = {}
            for i, ticker in enumerate(mercado_tickers):
                # Leemos de nuestra BD, NO de la API externa
                doc = db.db.collection('mercado').document(ticker).get()
                if doc.exists:
                    precio = doc.to_dict().get('precio_actual')
                    precios_locales[i+1] = (ticker, precio)
                    print(f"{i+1}. {ticker}: {precio:.2f}$")
            
            try:
                sel = int(input("\nNúmero de acción para comprar (0 para volver): "))
                if sel in precios_locales:
                    t_sel, p_sel = precios_locales[sel]
                    monto = float(input(f"¿Cuánto dinero ($) quieres invertir en {t_sel}?: "))
                    
                    cantidad = monto / p_sel
                    exito, nuevo_saldo = db.realizar_compra(t_sel, cantidad, p_sel)
                    
                    if exito:
                        print(f"\n✅ ¡Éxito! Has comprado {cantidad:.4f} unidades de {t_sel}.")
                    else:
                        print("\n❌ Error: Saldo insuficiente.")
            except Exception as e:
                print(f"⚠️ Error en la operación: {e}")

        elif opcion == '2':
                print("\n" + "-"*30)
                print("       TU CARTERA ACTUAL")
                print("-"*30)
                cartera = user_data.get('cartera', {})
                
                if not cartera:
                    print("No tienes activos todavía.")
                else:
                    opciones_venta = {}
                    for i, (ticker, cant) in enumerate(cartera.items()):
                        doc = db.db.collection('mercado').document(ticker).get()
                        p_act = doc.to_dict().get('precio_actual', 0) if doc.exists else 0
                        opciones_venta[i+1] = (ticker, cant, p_act)
                        print(f"{i+1}. {ticker:8} | Cant.: {cant:.4f} | Valor Actual: {cant*p_act:.2f}$")
                    
                    print("\n0. Volver")
                    try:
                        sel = int(input("\nSeleccione el número de acción para gestionar venta: "))
                        if sel in opciones_venta:
                            t_sel, c_max, p_sel = opciones_venta[sel]
                            
                            print(f"\nGestión de {t_sel} (Máx: {c_max:.4f} unidades)")
                            print(f"1. Vender 25% ({(c_max*0.25):.4f} ud)")
                            print(f"2. Vender 50% ({(c_max*0.50):.4f} ud)")
                            print(f"3. Vender 100% ({c_max:.4f} ud)")
                            print(f"4. Introducir cantidad manual")
                            
                            sub_opc = input("Seleccione opción de venta: ")
                            
                            c_vender = 0
                            if sub_opc == '1': c_vender = c_max * 0.25
                            elif sub_opc == '2': c_vender = c_max * 0.50
                            elif sub_opc == '3': c_vender = c_max
                            elif sub_opc == '4':
                                c_vender = float(input(f"¿Cuántas unidades quieres vender? (Máx {c_max:.4f}): "))
                            
                            if c_vender > 0:
                                exito, s_final = db.realizar_venta(t_sel, c_vender, p_sel)
                                if exito:
                                    print(f"\n✅ Venta completada. Has recibido {(c_vender*p_sel):.2f}$.")
                                    print(f"💰 Nuevo saldo total: {s_final:.2f}$")
                                else:
                                    print("❌ Error en la venta.")
                    except ValueError:
                        print("⚠️ Entrada no válida.")
        elif opcion == '3':
                break

if __name__ == "__main__":
    app_usuario()