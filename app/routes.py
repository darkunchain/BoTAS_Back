from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context
from ldap3 import Server, Connection, ALL, NTLM
import requests
import json
import re
from Crypto.Hash import MD4  # Importar MD4 desde pycryptodome
import time

def compute_md4_hash(password):
    md4 = MD4.new() # Crear un objeto MD4
    md4.update(password.encode('utf-16-le')) # Actualizar el objeto con la contraseña codificada en UTF-16-LE
    return md4.digest() # Obtener el hash en formato binario


def convertjson(valor):
    if isinstance(texto, list):
        texto = "\n".join(texto)
    # Asegúrate de que el texto sea una cadena
    if not isinstance(texto, str):
        raise ValueError("El texto debe ser una cadena o una lista de cadenas")

    # Limpia los corchetes y espacios adicionales
    texto = texto.strip('[]').strip()

    # Divídelo en partes por '-'
    partes = texto.split(' - ')

    # Crea un diccionario para almacenar los datos
    datos = {}

    # Procesa cada parte y añade al diccionario
    for vari in partes:
        clave_valor = vari.split(':', 1)
        if len(clave_valor) == 2:
            clave = clave_valor[0].strip()
            valor = clave_valor[1].strip()
            datos[clave] = valor

    # Añade la parte que no está separada por '-'
    clave_valor = datos.pop('DN', '').split(':', 1)
    if len(clave_valor) == 2:
        datos['DN'] = clave_valor[1].strip()

    # Convierte el diccionario a JSON
    json_data = json.dumps(datos, indent=4)

    print(json_data)




main = Blueprint('main', __name__)

@main.route('/verify_user', methods=['POST'])
def verify_user():
    data = request.json
    username = data.get('username')
    message = data.get('message')
    #Print('data: ', data, 'username: ', username, 'message: ', message)

    # Conectar a LDAP
    server = Server(current_app.config['LDAP_SERVER'], get_info=ALL)
    conn = Connection(server, user=current_app.config['LDAP_USER_DN'], password=current_app.config['LDAP_PASSWORD'], authentication=NTLM)
    conn.bind()
    if conn.bound:
        print("Conexión LDAP exitosa")
    else:
        print("Error en la conexión LDAP")
        return jsonify({'error': 'Error en la conexión LDAP'}), 500
    # Buscar el usuario en LDAP
    conn.search('dc=registraduria,dc=gov,dc=co', f'(sAMAccountName={username})', attributes=['sAMAccountName', 'displayName', 'department', 'telephoneNumber', 'mail'])
    user_info = conn.entries
    print('user_info: ', user_info)

    if not user_info:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    user_info = user_info[0]

    lm_studio_url = "http://172.20.34.66:1234/v1/chat/completions"  # Ajusta la URL según LM Studio
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "messages": [
            {"role": "user", "content": "Responde siempre en español. " + message}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": True
    }

    def generate():
        try:
            response = requests.post(lm_studio_url, json=data, headers=headers, stream=True)
            response.raise_for_status()  # Lanza una excepción si hay un error HTTP

            # Procesar la respuesta en fragmentos
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    # Decodificar el fragmento
                    decoded_chunk = chunk.decode('utf-8')
                    print('decode chunk: ', decoded_chunk)

                    # Manejar el fragmento especial "[DONE]"
                    if decoded_chunk.strip() == 'data: [DONE]':
                        print("Generación completada.")
                        continue  # Ignorar este fragmento

                    # Eliminar el prefijo "data: " si está presente
                    if decoded_chunk.startswith('data: '):
                        decoded_chunk = decoded_chunk.replace('data: ', '')

                    # Parsear el fragmento como JSON
                    try:
                        json_data = json.loads(decoded_chunk)
                        print('json_data: ', json_data)

                        # Extraer el contenido del fragmento
                        if json_data.get("choices") and json_data["choices"][0].get("delta"):
                            content = json_data["choices"][0]["delta"].get("content", "")
                            print('content (original): ', content)

                            # Enviar el contenido al frontend sin agregar espacios adicionales
                            if content:
                                yield f"data: {json.dumps({'content': content})}\n\n"
                    except json.JSONDecodeError as e:
                        print(f"Error al parsear JSON: {e}")

        except requests.exceptions.RequestException as e:
            yield f"data: {json.dumps({'error': f'Error with LM Studio: {str(e)}'})}\n\n"

    # Devolver la respuesta en streaming
    return Response(stream_with_context(generate()), content_type='text/event-stream')