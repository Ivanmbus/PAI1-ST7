# common/crypto_utils.py
"""
Utilidades criptográficas compartidas
"""
import hmac
import hashlib
import secrets
from typing import Tuple
from .constantes import NONCE_SIZE, MAC_SIZE

def generar_nonce() -> bytes:
    """
    Genera un NONCE criptográficamente seguro
    
    Returns:
        bytes: NONCE de 32 bytes
    """
    return secrets.token_bytes(NONCE_SIZE)

def calcular_mac(clave: bytes, mensaje: bytes, nonce: bytes) -> bytes:
    """
    Calcula el MAC de un mensaje usando HMAC-SHA256
    Incluye el mensaje y el NONCE para asegurar la unicidad del MAC y evitar ataques de repetición
    Args:
        clave: Clave compartida
        mensaje: Datos a proteger
        nonce: NONCE único para este mensaje
    
    Returns:
        bytes: MAC de 32 bytes
    """
    datos = mensaje + nonce
    return hmac.new(clave, datos, hashlib.sha256).digest()

def verificar_mac(clave: bytes, mensaje: bytes, nonce: bytes, mac_recibido: bytes) -> bool:
    """
    Verifica el MAC de un mensaje usando comparación en tiempo constante
    
    Args:
        clave: Clave compartida
        mensaje: Datos recibidos
        nonce: NONCE recibido
        mac_recibido: MAC recibido del cliente
    
    ⚠️ NOTA: Esta función NO verifica replay attacks.
    Para validación completa, usar servidor.crypto_server.verificar_mensaje_completo()

    Returns:
        bool: True si el MAC es válido
    """
    mac_calculado = calcular_mac(clave, mensaje, nonce)
    return hmac.compare_digest(mac_calculado, mac_recibido)