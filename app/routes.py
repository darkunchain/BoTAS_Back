from flask import Blueprint, request, jsonify, current_app
from ldap3 import Server, Connection, ALL, NTLM
import requests
import json
import re


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
    server = Server(current_app.config['LDAP_SERVER'], get_info=ALL)
    conn = Connection(server, user=current_app.config['LDAP_USER_DN'], password=current_app.config['LDAP_PASSWORD'], authentication=NTLM)
    conn.bind()
    
    # Buscar el usuario en LDAP
    conn.search('dc=registraduria,dc=gov,dc=co', f'(sAMAccountName={username})', attributes=['sAMAccountName','displayName','department','telephoneNumber','mail'])
    user_info = conn.entries
    print(f'user_info: {user_info}')
    # Suponiendo que conn.entries es una lista de objetos Entry
    # Aquí defines los atributos que deseas obtener
    atributos_deseados = ['sAMAccountName','displayName','department','telephoneNumber','mail']

    # Lista donde almacenaremos las entradas transformadas a diccionarios
    usuarios = []

    for entry in conn.entries:
        usuario = {}
        for atributo in atributos_deseados:
            # Verificamos que el atributo esté presente antes de intentar acceder a él
            if atributo in entry:
                # Convertimos los valores de LDAP a listas de Python si es necesario
                if isinstance(entry[atributo], list):
                    usuario[atributo] = entry[atributo]
                else:
                    usuario[atributo] = [entry[atributo].value]

        # Agregamos el usuario al listado final
        usuarios.append(usuario)
        print(f'usuarios: {usuarios}')

    # Convertimos la lista de usuarios a formato JSON
    usuarios_json = json.dumps(usuarios)

    print(f'usuarios_json: {usuarios_json}')

    
    #convertjson(user_info)
    
    
    if not user_info:
        return jsonify({'error': 'User not found'}), 404

    # Supongamos que solo hay un resultado
    user_info = user_info[0]

    # Enviar mensaje al modelo de Ollama
    response = requests.post(current_app.config['OLLAMA_API_URL'], json={'message': message})
    
    if response.status_code != 200:
        return jsonify({'error': 'Error with Ollama model'}), 500

    model_response = response.json()

    return jsonify({
        'user_info': {
            'displayName': user_info.displayName.value,
            'mail': user_info.mail.value
        },
        'model_response': model_response
    })
