from flask import Flask, request, jsonify
import random
import requests

app = Flask(__name__)

# Configuración de la API
API_KEY = 'TFZLE-zNVoz-R8vcM-gFi0Y-z2Ta6-smhlK'  # Reemplaza con tu clave
SERVICE_ID = '5'
URL = 'https://alpha.imeicheck.com/api/php-api/create'

# Función Luhn para validar IMEI
def is_valid_imei(imei):
    total = 0
    reverse_digits = imei[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n = n * 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

# Llamada directa a la API para obtener la respuesta sin modificar
def check_imei(imei):
    try:
        response = requests.get(URL, params={'key': API_KEY, 'service': SERVICE_ID, 'imei': imei})
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error al conectar con la API: {str(e)}")
        return None

# Generador de IMEIs basado en uno existente
def generate_imei_from_base(base_imei):
    random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return base_imei[:8] + random_suffix

# Ruta principal para los comandos
@app.route('/generate_imei', methods=['POST'])
def generate_imei():
    data = request.form
    if 'message' not in data:
        return jsonify({'error': 'Mensaje no recibido'}), 400

    message = data['message']
    sender = data.get('sender', 'Usuario Desconocido')

    # Comando 'menu'
    if message.lower() == 'menu':
        menu_response = (
            "\n💀 *[DC-UNLOCK-X] Menú de Opciones*\n\n"
            "✅ *Comandos disponibles:*\n"
            "1️⃣ **Generar y Verificar IMEI**\n"
            "- Comando: `f4 [número IMEI]`\n"
            "- Verifica si el IMEI es válido y genera 5 nuevos IMEIs basados en el mismo.\n"
            "- **Ejemplo:** `f4 123456789012345`\n\n"
            "2️⃣ **Blacklist Status**\n"
            "- Comando: `bl [número IMEI]`\n"
            "- Verifica si el IMEI está en la lista negra.\n"
            "- **Ejemplo:** `bl 123456789012345`"
        )
        print("Comando 'menu' recibido. Enviando opciones al usuario...")
        return jsonify({'reply': menu_response}), 200

    # Comando 'bl' para verificar lista negra
    if message.lower().startswith('bl') and len(message.split()) == 2:
        imei = message.split()[1]
        print(f"Comando 'bl' recibido. IMEI a verificar: {imei}")

        # Validación Luhn
        if not is_valid_imei(imei):
            return jsonify({'reply': "❌ *IMEI inválido*. No pasa la verificación Luhn."}), 200

        # Llamada a la API
        api_response = check_imei(imei)

        if api_response and api_response['status'] == 'success':
            brand = api_response['object'].get('brand', 'Desconocido')
            model = api_response['object'].get('model', 'Desconocido')
            model_name = api_response['object'].get('name', 'Desconocido')
            blacklist_status = 'Limpio ✅' if not api_response['object'].get('gsmaBlacklisted', True) else 'En lista negra ❌'

            response_message = (
                "\n💀 *[DC-UNLOCK-X] Blacklist Status*\n\n"
                f"✅ *IMEI: {imei}*\n"
                f"✅ *Marca: {brand}*\n"
                f"✅ *Modelo: {model}*\n"
                f"✅ *Nombre del Modelo: {model_name}*\n"
                f"✅ *Estado de la lista negra: {blacklist_status}*\n"
            )
            print(f"Respuesta de la API para 'bl': {response_message}")
            return jsonify({'reply': response_message}), 200
        else:
            return jsonify({'reply': "⚠️ *Error al verificar el IMEI. Intente más tarde.*"}), 200

    # Comando 'f4' para generar IMEIs
    if message.lower().startswith('f4') and len(message.split()) == 2:
        base_imei = message.split()[1]
        print(f"Comando 'f4' recibido. IMEI base: {base_imei}")

        if not is_valid_imei(base_imei):
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
        print(f"Respuesta para 'f4': {response_message}")
        return jsonify({'reply': response_message}), 200

    return jsonify({'error': 'Formato incorrecto. Usa: f4 IMEI o bl IMEI'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
