from flask import Blueprint, request, jsonify, current_app
from ldap3 import Server, Connection, ALL, NTLM
import os
from dotenv import load_dotenv
import requests
import json
import re

load_dotenv('/.env')

print("Variables de entorno cargadas:")
for key, value in os.environ.items():
    print(f"{key}: {value}")

ldap_server = os.getenv('LDAP_SERVER')
ldap_user_dn = os.getenv('LDAP_USER_DN')
ldap_password = os.getenv('LDAP_PASSWORD')


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

    # Conectar a LDAP
    print('ldap_server:'+ ldap_server)
    server = Server(current_app.config[ldap_server], get_info=ALL)
    conn = Connection(server, user=current_app.config[ldap_user_dn], password=current_app.config[ldap_password], authentication=NTLM)
    conn.bind()
    # Buscar el usuario en LDAP
    conn.search('dc=registraduria,dc=gov,dc=co', f'(sAMAccountName={username})', attributes=['sAMAccountName','displayName','department','telephoneNumber','mail'])
    user_info = conn.entries

    if not user_info:
        return jsonify({'error': 'User not found'}), 404

    user_info = user_info[0]

    lm_studio_url = "http://localhost:1234/v1/chat/completions"  # Ajusta la URL según LM Studio
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "messages": [
            {"role": "user", "content": message}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    try:
        response = requests.post(lm_studio_url, json=data, headers=headers)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP
        model_response = response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error with LM Studio: {str(e)}'}), 500

    return jsonify({
        'user_info': {
            'displayName': user_info.displayName.value,
            'mail': user_info.mail.value
        },
        'model_response': model_response
    })
