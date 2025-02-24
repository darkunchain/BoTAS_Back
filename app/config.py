from dotenv import load_dotenv
import os

""" print("Variables de entorno cargadas:")
for key, value in os.environ.items():
    print(f"{key}: {value}")
"""


# Cargar las variables de entorno desde el archivo .env
load_dotenv(override=True)


class Config:
   LDAP_SERVER = os.getenv('LDAP_SERVER')
   LDAP_USER_DN = os.getenv('LDAP_USER_DN')
   LDAP_PASSWORD = os.getenv('LDAP_PASSWORD')
   OLLAMA_API_URL = os.getenv('OLLAMA_API_URL')


