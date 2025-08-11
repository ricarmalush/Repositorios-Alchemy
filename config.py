# config.py

import os
from dotenv import load_dotenv

load_dotenv() # Carga las variables de entorno del archivo .env

class Config:
    # Obtener variables de la base de datos del archivo .env
    DB_USER = os.getenv("DB_USER", "root") # Valor por defecto 'root' si no se especifica
    DATABASE_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost") # Valor por defecto 'localhost'
    DB_PORT = os.getenv("DB_PORT", "3306")     # Valor por defecto '3306'
    DB_NAME = os.getenv("DB_NAME", "alchemy_regadio") # Valor por defecto 'alchemy_regadio'

    # Validar que las variables críticas existan
    if not DATABASE_PASSWORD:
        raise ValueError("DB_PASSWORD no está definida en el archivo .env")
    if not DB_USER:
        raise ValueError("DB_USER no está definida en el archivo .env")
    if not DB_HOST:
        raise ValueError("DB_HOST no está definida en el archivo .env")
    if not DB_PORT:
        raise ValueError("DB_PORT no está definida en el archivo .env")
    if not DB_NAME:
        raise ValueError("DB_NAME no está definida en el archivo .env")

    # Construir la URL de conexión a la base de datos de SQLAlchemy
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DATABASE_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

config = Config()