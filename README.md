# BoTAS_Back
Backend BoTAS

Instalacion Inicial:

crear un entorno virtual de Python para no afectar la configuracion y los paquetes globales en el equipo
python -m venv venv

Habilitar el entorno virtual
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`

se crea la estructura basica de archivos:

BoTAS_Back/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   └── config.py
│
├── instance/
│   └── config.py
│
├── venv/
│
├── .env
├── .gitignore
├── run.py
└── requirements.txt
