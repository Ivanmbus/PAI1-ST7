# servidor/autenticacion.py
"""
Lógica de autenticación: registro y login
"""
import logging
from typing import Tuple, Optional

from server.database import DatabaseManager
from server.crypto_server import hashear_password, verificar_password

logger = logging.getLogger(__name__)

class Autenticacion:
    """Gestiona registro y login de usuarios"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def registrar(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Registra un nuevo usuario
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        # Validar que el usuario no exista
        if self.db.usuario_existe(username):
            logger.warning(f"[WARNING]  Intento de registro con usuario existente: {username}")
            return False, "El usuario ya existe"
        
        # Hashear contraseña con Argon2id
        try:
            password_hash = hashear_password(password)
        except Exception as e:
            logger.error(f"[ERROR] Error al hashear contraseña: {e}")
            return False, "Error al procesar la contraseña"
        
        # Crear usuario en BD
        if self.db.crear_usuario(username, password_hash):
            logger.info(f"[OK] Usuario registrado: {username}")
            return True, "Usuario registrado exitosamente"
        else:
            logger.error(f"[ERROR] Error al crear usuario: {username}")
            return False, "Error al crear el usuario"
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Autentica un usuario
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        # Verificar que el usuario exista
        password_hash = self.db.obtener_password_hash(username)
        if not password_hash:
            logger.warning(f"[WARNING]  Intento de login con usuario inexistente: {username}")
            # Mensaje genérico por seguridad (no revelar si existe)
            return False, "Credenciales incorrectas"
        
        # Verificar contraseña en tiempo constante
        if verificar_password(password_hash, password):
            logger.info(f"[OK] Login exitoso: {username}")
            return True, "Login exitoso"
        else:
            logger.warning(f"[WARNING]  Contraseña incorrecta para usuario: {username}")
            return False, "Credenciales incorrectas"