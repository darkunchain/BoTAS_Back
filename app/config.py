from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()


class Config:
   LDAP_SERVER = os.getenv('LDAP_SERVER')
   LDAP_USER_DN = os.getenv('LDAP_USER_DN')
   LDAP_PASSWORD = os.getenv('LDAP_PASSWORD')
   OLLAMA_API_URL = os.getenv('OLLAMA_API_URL')


