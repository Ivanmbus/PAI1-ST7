# common/config.py
"""
Gestión de configuración
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import base64

load_dotenv()

class Config:
    # Red
    SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 5000))
    
    # Base de datos
    DB_PATH = os.getenv("DB_PATH", "./database/usuarios.db")
    
    # Logs
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/servidor.log")
    
    # Clave compartida (en base64)
    SHARED_KEY_B64 = os.getenv("SHARED_KEY")
    
    @classmethod
    def get_shared_key(cls) -> bytes:
        """Obtiene la clave compartida decodificada"""
        if cls.SHARED_KEY_B64:
            return base64.b64decode(cls.SHARED_KEY_B64)
        # Si no existe, cargar desde archivo
        key_path = Path("config/shared_key.key")
        if key_path.exists():
            return key_path.read_bytes()
        raise ValueError("No se encontró la clave compartida")