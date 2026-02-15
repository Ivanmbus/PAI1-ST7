# cliente/crypto_client.py
"""
Funciones criptográficas del cliente
"""
import logging
from typing import Tuple

from common.crypto__utils import generar_nonce, calcular_mac

logger = logging.getLogger(__name__)

def preparar_mensaje_seguro(
    clave: bytes,
    mensaje: bytes
) -> Tuple[bytes, bytes, bytes]:
    """
    Prepara un mensaje con protección de integridad
    
    Args:
        clave: Clave compartida con el servidor
        mensaje: Datos a enviar (JSON serializado)
    
    Returns:
        Tuple[bytes, bytes, bytes]: (mensaje, mac, nonce)
    
    Proceso:
        1. Genera NONCE único
        2. Calcula MAC = HMAC(clave, mensaje + nonce)
        3. Retorna (mensaje, mac, nonce)
    
    Ejemplo:
        >>> clave = Config.get_shared_key()
        >>> mensaje = b'{"tipo":"login","datos":{...}}'
        >>> msg, mac, nonce = preparar_mensaje_seguro(clave, mensaje)
    """
    # Generar NONCE único
    nonce = generar_nonce()
    logger.debug(f" NONCE generado: {nonce.hex()[:16]}...")
    
    # Calcular MAC
    mac = calcular_mac(clave, mensaje, nonce)
    logger.debug(f"[LOCK] MAC calculado: {mac.hex()[:16]}...")
    
    return mensaje, mac, nonce