# servidor/crypto_server.py
"""
Funciones de validación COMPLETA en el servidor
Incluye verificación de integridad (MAC) + anti-replay (NONCE)
"""
import hmac
import logging
from typing import Tuple, Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from common.crypto__utils import verificar_mac
from common.constantes import (
    ARGON2_TIME_COST,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_HASH_LEN,
    ARGON2_SALT_LEN
)

logger = logging.getLogger(__name__)

# Configurar Argon2
ph = PasswordHasher(
    time_cost=ARGON2_TIME_COST,
    memory_cost=ARGON2_MEMORY_COST,
    parallelism=ARGON2_PARALLELISM,
    hash_len=ARGON2_HASH_LEN,
    salt_len=ARGON2_SALT_LEN
)

# ===================================================================
# VALIDACIÓN COMPLETA DE MENSAJES (MAC + NONCE)
# ===================================================================

class MensajeInvalido(Exception):
    """Excepción cuando un mensaje no pasa las validaciones"""
    pass

def verificar_mensaje_completo(
    db_manager,
    clave: bytes,
    mensaje: bytes,
    nonce: bytes,
    mac_recibido: bytes
) -> bool:
    """
    Validación COMPLETA de un mensaje con protección anti-replay
    
    Verifica en orden:
    1. Integridad del MAC (detecta modificaciones - Man-in-the-Middle)
    2. NONCE no usado previamente (detecta replay attacks)
    
    Args:
        db_manager: Instancia de DatabaseManager (para validar NONCE)
        clave: Clave compartida
        mensaje: Datos recibidos
        nonce: NONCE recibido
        mac_recibido: MAC recibido del cliente
    
    Returns:
        bool: True si el mensaje es válido
    
    Raises:
        MensajeInvalido: Si falla alguna validación
    
    Ejemplo:
        >>> from servidor.database import DatabaseManager
        >>> db = DatabaseManager("usuarios.db")
        >>> 
        >>> try:
        >>>     if verificar_mensaje_completo(db, clave, msg, nonce, mac):
        >>>         print("[OK] Mensaje válido - procesar")
        >>> except MensajeInvalido as e:
        >>>     print(f"[ERROR] Mensaje rechazado: {e}")
    """
    
    # PASO 1: Verificar integridad (MAC)
    if not verificar_mac(clave, mensaje, nonce, mac_recibido):
        logger.warning("[ERROR] MAC inválido - Posible ataque Man-in-the-Middle")
        raise MensajeInvalido("MAC inválido - Integridad comprometida")
    
    logger.debug("[OK] MAC válido - Integridad verificada")
    
    # PASO 2: Verificar que el NONCE no ha sido usado (anti-replay)
    if not db_manager.validar_nonce(nonce):
        logger.warning(
            f"[ERROR] NONCE duplicado detectado - REPLAY ATTACK! NONCE: {nonce.hex()[:16]}..."
        )
        raise MensajeInvalido("NONCE ya usado - Replay attack detectado")
    
    logger.debug(f"[OK] NONCE válido y registrado: {nonce.hex()[:16]}...")
    
    # TODAS LAS VALIDACIONES PASADAS
    logger.info("[OK] Mensaje completamente validado (MAC + NONCE)")
    return True



# ===================================================================
# GESTIÓN DE CONTRASEÑAS (Argon2id)
# ===================================================================

def hashear_password(password: str) -> str:
    """
    Genera hash Argon2id de una contraseña
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        str: Hash de la contraseña (incluye salt automáticamente)
    """
    return ph.hash(password)


def verificar_password(password_hash: str, password: str) -> bool:
    """
    Verifica una contraseña contra su hash
    
    Args:
        password_hash: Hash almacenado en BD
        password: Contraseña proporcionada por el usuario
    
    Returns:
        bool: True si la contraseña es correcta
    """
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False


def secure_compare(a: bytes, b: bytes) -> bool:
    """
    Comparación en tiempo constante (protección contra timing attacks)
    
    Args:
        a: Primer valor
        b: Segundo valor
    
    Returns:
        bool: True si son iguales
    """
    return hmac.compare_digest(a, b)