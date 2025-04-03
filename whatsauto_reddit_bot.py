from flask import Flask, request, jsonify
import random
import requests
import os  # Importante para obtener variables de entorno
@app.route("/", methods=["GET"])
def home():
    return "WhatsAuto Reddit Bot está funcionando correctamente", 200
app = Flask(__name__)

# Configuración de la API de IMEI Check
API_KEY = 'TFZLE-zNVoz-R8vcM-gFi0Y-z2Ta6-smhlK'  # Reemplaza con tu clave de acceso
SERVICE_ID = '5'  # ID de servicio que te dieron
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

# Endpoint para manejar los comandos 'bl', 'f4', 'fmi' y 'menu'
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

    # Comando 'menu' para mostrar las opciones disponibles
    if message.lower() == 'menu':
        print("Comando 'menu' recibido.")
        menu_response = (
            "\n💀 *[DC-UNLOCK-X] Menu de Opciones*\n\n"
            "✅ *Alternativas disponibles:*\n"
            "1️⃣ **Generar y Verificar IMEI**\n"
            "- Comando: `f4 [número IMEI]`\n"
            "- Este comando verifica si un IMEI es válido y genera 5 nuevos IMEIs basados en el IMEI proporcionado.\n"
            "- **Ejemplo:** `f4 123456789012345`\n\n"
            "2️⃣ **Blacklist Status**\n"
            "- Comando: `bl [número IMEI]`\n"
            "- Este comando verifica si el IMEI está en la lista negra de la base de datos.\n"
            "- **Ejemplo:** `bl 123456789012345`\n\n"
            "3️⃣ **Buscar mi iPhone Status**\n"
            "- Comando: `fmi [número IMEI]`\n"
            "- Este comando verifica si 'Buscar mi iPhone' está activado o desactivado.\n"
            "- **Ejemplo:** `fmi 354848091889059`"
        )
        return jsonify({'reply': menu_response}), 200

    # Comando 'fmi' para verificar el estado de 'Buscar mi iPhone'
    if message.lower().startswith('fmi') and len(message.split()) == 2:
        imei = message.split()[1]
        print(f"Comando 'fmi' recibido con IMEI: {imei}")
        if not is_valid_imei(imei):
            print(f"IMEI no válido: {imei}")
            return jsonify({'reply': "❌ *IMEI inválido*. No pasa la verificación Luhn."}), 200

        response_message, success = check_fmi(imei)

        if success:
            return jsonify({'reply': response_message}), 200
        else:
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
        )

        return jsonify({'reply': response_message}), 200

    print("Comando no reconocido.")
    return jsonify({'error': 'Formato incorrecto. Usa: f4 IMEI, bl IMEI o fmi IMEI'}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render asigna dinámicamente el puerto
    app.run(host="0.0.0.0", port=port)




