from flask import Flask, request, jsonify
import random
import requests
import os  # Importante para obtener variables de entorno
import threading
import time

app = Flask(__name__)  # Definir la app antes de los decoradores @app.route

@app.route("/", methods=["GET"])
def home():
    return "WhatsAuto Reddit Bot está funcionando correctamente", 200

# Función para evitar inactividad enviando un ping cada 5 minutos
def auto_ping():
    url = "https://whatsbot-4uk2.onrender.com"
    timeout = 3  # Reducimos el timeout a 3 segundos para evitar bloqueos largos
    interval = 120  # Hacemos ping cada 2 minutos en lugar de esperar demasiado
    
    while True:
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                print("✅ Ping enviado correctamente")
            else:
                print(f"⚠️ Ping fallido. Código de estado: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error en el auto-ping: {e}")
        
        time.sleep(interval)  # Esperamos el tiempo antes de hacer otro ping

# Ejecutar el auto-ping en un hilo separado
import threading
threading.Thread(target=auto_ping, daemon=True).start()

# Configuración de la API de IMEI Check
API_KEY = 'TFZLE-zNVoz-R8vcM-gFi0Y-z2Ta6-smhlK'  # Reemplaza con tu clave de acceso
SERVICE_ID = '5'  # ID de servicio que te dieron
CHECK_SERVICE_ID = '39'  # ID de servicio para el comando 'check'
URL = 'https://alpha.imeicheck.com/api/php-api/create'  # URL para la API

# Configuración de la API FMI
FMI_URL = 'https://alpha.imeicheck.com/api/php-api/create'  # La misma URL para la API FMI
FMI_SERVICE_ID = '1'  # ID de servicio para FMI (puede variar según tu API)

# Función para validar el IMEI usando el algoritmo de Luhn
def is_valid_imei(imei):
    total = 0
    reverse_digits = imei[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:  # Si la posición es impar (según el algoritmo Luhn)
            n = n * 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0
# ✅ Función para validar un número de serie (serial)
def is_valid_serial(serial):
    return serial.isalnum() and len(serial) >= 8

# Función para verificar el IMEI en la API de IMEI Check y devolver la respuesta limpia
def check_imei(imei):
    try:
        print(f"Consultando IMEI en la API: {imei}")
        response = requests.get(f'{URL}', params={'key': API_KEY, 'service': SERVICE_ID, 'imei': imei})
        response.raise_for_status()  # Asegura que la petición fue exitosa
        data = response.json()

        print(f"Respuesta de la API: {data}")

        if data and data['status'] == 'success':
            result = data['result']
            result = result.replace("<br>", "\n").replace("<span style='color:green;'>", "").replace("</span>", "")

            imei = data['imei']
            brand = data['object']['brand']
            model = data['object']['model']
            model_name = data['object']['name']
            blacklist_status = 'Limpio' if not data['object']['gsmaBlacklisted'] else 'En Lista Negra'
            
            formatted_response = (
                "\n💀 *[DC-UNLOCK-X] Blacklist Status*\n\n"
                f"✅ *IMEI: {imei}*\n"
                f"✅ *Marca: {brand}*\n"
                f"✅ *Modelo: {model}*\n"
                f"✅ *Nombre del Modelo: {model_name}*\n"
                f"✅ *Estado de la lista negra: {blacklist_status}*\n"
                "\n *ByDegoServ*"
                
            )
            return formatted_response, True
        else:
            print(f"Error en la respuesta: {data}")
            return "⚠️ *En Mantenimiento* - Vuelva más tarde.", False
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        return "⚠️ *En Mantenimiento* - Vuelva más tarde.", False

# Función para verificar el estado de 'Buscar mi iPhone' usando la API de FMI
def check_fmi(imei):
    try:
        print(f"Consultando FMI en la API: {imei}")
        response = requests.get(f'{FMI_URL}', params={'key': API_KEY, 'service': FMI_SERVICE_ID, 'imei': imei})
        response.raise_for_status()  # Asegura que la petición fue exitosa
        data = response.json()

        print(f"Respuesta de FMI API: {data}")

        if data and data['status'] == 'success':
            result = data['result']
            result = result.replace("<br>", "\n").replace("<span style='color:red;'>", "").replace("</span>", "")
            
            imei = data['imei']
            model = data['object']['model']
            fmi_status = '❌ ACTIVADO' if data['object']['fmiOn'] else '✅ DESACTIVADO'

            formatted_response = (
                "\n💀 *[DC-UNLOCK-X] Buscar mi iPhone Status*\n\n"
                f"✅ *IMEI: {imei}*\n"
                f"✅ *Modelo: {model}*\n"
                f"✅ *Buscar mi iPhone: {fmi_status}*\n"
                "\n *ByDegoServ*"
            )
            return formatted_response, True
        else:
            print(f"Error en la respuesta: {data}")
            return "⚠️ *En Mantenimiento* - Vuelva más tarde.", False
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        return "⚠️ *En Mantenimiento* - Vuelva más tarde.", False

# Función para generar IMEIs nuevos a partir de un IMEI base (solo ejemplo)
def generate_imei_from_base(base_imei):
    random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return base_imei[:8] + random_suffix

def check_full_imei_details(imei_or_serial):
    try:
        print(f"Consultando en la API para detalles completos: {imei_or_serial}")
        response = requests.get(f'{URL}', params={'key': API_KEY, 'service': CHECK_SERVICE_ID, 'imei': imei_or_serial})
        response.raise_for_status()
        data = response.json()

        print(f"Respuesta completa de la API: {data}")

        if data and data['status'] == 'success':
            imei_data = data['object']
            
            model_description = imei_data.get('modelDesc', 'Desconocido')
            model = imei_data.get('model', 'Desconocido')
            country = imei_data.get('country', 'Desconocido')
            imei2 = imei_data.get('imei2', 'Desconocido')
            serial = imei_data.get('serial', 'Desconocido')
            activated = 'Activado' if imei_data.get('activated', False) else 'No Activado'
            warranty_status = imei_data.get('warrantyStatus', 'Desconocido')
            coverage_start_date = imei_data.get('coverageStartDate', 'Desconocido')
            estimated_purchase_date = imei_data.get('estPurchaseDate', 'Desconocido')
            applecare_eligible = 'Sí' if not imei_data.get('acEligible', False) else 'No'
            fmi_status = 'ON' if imei_data.get('fmiOn', False) else 'OFF'
            blacklist_status = 'Limpio' if not imei_data.get('gsmaBlacklisted', False) else 'En lista negra'
            carrier = imei_data.get('carrier', 'Desconocido')
            simlock = 'Desbloqueado' if not imei_data.get('simlock', False) else 'Bloqueado'

            formatted_response = (
                "\n💀 *[DC-UNLOCK-X] Check Completo IMEI/Serial*\n\n"
                f"✅ *Descripción del Modelo:* {model_description}\n"
                f"✅ *Modelo:* {model}\n"
                f"✅ *Región del Modelo:* {country}\n"
                f"✅ *Número IMEI2:* {imei2}\n"
                f"✅ *Número de Serie:* {serial}\n"
                f"✅ *Estado de Activación:* {activated}\n"
                f"✅ *Estado de Garantía:* {warranty_status}\n"
                f"✅ *Fecha de Inicio de Cobertura:* {coverage_start_date}\n"
                f"✅ *Fecha Estimada de Compra:* {estimated_purchase_date}\n"
                f"✅ *Elegibilidad AppleCare:* {applecare_eligible}\n"
                f"✅ *Estado FMI:* {fmi_status}\n"
                f"✅ *Estado de la Lista Negra:* {blacklist_status}\n"
                f"✅ *Operador:* {carrier}\n"
                f"✅ *Estado del Sim-Lock:* {simlock}\n"
                "\n *ByDegoServ*"
            )
            return formatted_response, True
        else:
            return "⚠️ *Error al obtener detalles completos del IMEI o serial.*", False
    except requests.exceptions.RequestException as e:
        print(f"Error al consultar el IMEI o serial completo: {e}")
        return "⚠️ *Error al obtener detalles completos del IMEI o serial.*", False


# Endpoint para manejar los comandos 'bl', 'f4', 'fmi', 'check' y 'menu'
@app.route('/generate_imei', methods=['POST'])
def generate_imei():
    data = request.form
    print(f"Datos recibidos: {data}")
    
    if 'message' not in data:
        print("Error: No se recibió un mensaje.")
        return jsonify({'error': 'Mensaje no recibido'}), 400

    message = data['message']
    sender = data.get('sender', 'Usuario Desconocido')

    # Comando 'bl' para verificar el IMEI en la lista negra
    if message.lower().startswith('bl') and len(message.split()) == 2:
        imei = message.split()[1]
        print(f"Comando 'bl' recibido con IMEI: {imei}")
        if not is_valid_imei(imei):
            print(f"IMEI no válido: {imei}")
            return jsonify({'reply': "❌ *IMEI inválido*. No pasa la verificación Luhn."}), 200

        response_message, success = check_imei(imei)

        if success:
            return jsonify({'reply': response_message}), 200
        else:
            return jsonify({'reply': response_message}), 200

# Comando 'check' para obtener los detalles completos del IMEI o Serial
    if message.lower().startswith('check') and len(message.split()) == 2:
        imei = message.split()[1]
        print(f"Comando 'check' recibido con dato: {imei}")

        if imei.isdigit() and is_valid_imei(imei):
            print(f"IMEI válido detectado: {imei}")
            response_message, success = check_full_imei_details(imei)

        elif is_valid_serial(imei):
            print(f"Serial válido detectado: {imei}")
            response_message, success = check_full_imei_details(imei)

        else:
            print(f"Ni IMEI ni Serial válidos: {imei}")
            return jsonify({'reply': "❌ *Los datos ingresados no corresponden a una orden válida. Verifica por favor.*"}), 200

        return jsonify({'reply': response_message}), 200


    # Comando 'menu' para mostrar las opciones disponibles
    if message.lower() == 'menu':
        print("Comando 'menu' recibido.")
        menu_response = (
            "\n💀 *MGSM OPCIONES CHECK*\n\n"
"✅ *Alternativas disponibles:*\n"
"1️⃣ *Generar y Verificar IMEI*\n"
"- Comando: `f4 [IMEI]`\n"
"- Verifica el IMEI y genera 5 nuevos similares.\n"
"- *Ejemplo:* `f4 123456789012345`\n\n"
"2️⃣ *Dc Un Check Blacklist Global*\n"
"- Comando: `bl [IMEI]`\n"
"- Comprueba si el IMEI está en blacklist.\n"
"- *Ejemplo:* `bl 123456789012345`\n\n"
"3️⃣ *FMI (Find My...)*\n"
"- Comando: `fmi [IMEI|SN]`\n"
"- Verifica si FMI está ACTIVADO o DESACTIVADO.\n"
"- *Ejemplo:* `fmi 354848091889059`\n\n"
"4️⃣ *Check Completo*\n"
"- Comando: `check [IMEI|SN]`\n"
"- Muestra información completa del IMEI/SN.\n"
"- *Ejemplo:* `check 123456789012345`\n\n"
"*DcUnlockyTecArg*"

        )
        return jsonify({'reply': menu_response}), 200

    # Comando 'fmi' para verificar el estado de 'Buscar mi iPhone'
    if message.lower().startswith('fmi') and len(message.split()) == 2:
        dato = message.split()[1]
        print(f"Comando 'fmi' recibido con dato: {dato}")
        
        if dato.isdigit() and is_valid_imei(dato):
            print(f"IMEI válido detectado: {dato}")
            response_message, success = check_fmi(dato)
        elif is_valid_serial(dato):
            print(f"Serial válido detectado: {dato}")
            response_message, success = check_fmi(dato)
        else:
            print(f"Ni IMEI ni Serial válidos: {dato}")
            return jsonify({'reply': "❌ *Los datos ingresados no corresponden a un IMEI o Serial válido.*"}), 200

        return jsonify({'reply': response_message}), 200


    # Comando 'f4' para generar IMEIs nuevos
    if message.lower().startswith('f4') and len(message.split()) == 2:
        base_imei = message.split()[1]
        print(f"Comando 'f4' recibido con IMEI base: {base_imei}")
        if not is_valid_imei(base_imei):
            print(f"IMEI no válido: {base_imei}")
            return jsonify({'reply': "❌ *IMEI inválido*. No pasa la verificación Luhn."}), 200

        imeis = [generate_imei_from_base(base_imei) for _ in range(5)]
        response_message = (
            "\n💀 *[DC-UNLOCK-X] IMEI Gen Ready*\n\n"
            "✅ *Alternativas Generadas:*\n"
            f"1️⃣ `{imeis[0]}`\n"
            f"2️⃣ `{imeis[1]}`\n"
            f"3️⃣ `{imeis[2]}`\n"
            f"4️⃣ `{imeis[3]}`\n"
            f"5️⃣ `{imeis[4]}`\n"
            "\n *ByDegoServ*"
        )

        return jsonify({'reply': response_message}), 200

    print("Comando no reconocido.")
    return jsonify({'error': 'Formato incorrecto. Usa: f4 IMEI, bl IMEI, fmi IMEI o check IMEI'}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render asigna dinámicamente el puerto
    app.run(host="0.0.0.0", port=port)




