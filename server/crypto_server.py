# servidor/crypto_server.py
"""
Funciones criptográficas del servidor
"""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import hmac
from common.constantes import (
    ARGON2_TIME_COST,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_HASH_LEN,
    ARGON2_SALT_LEN
)

# Configurar Argon2
ph = PasswordHasher(
    time_cost=ARGON2_TIME_COST,
    memory_cost=ARGON2_MEMORY_COST,
    parallelism=ARGON2_PARALLELISM,
    hash_len=ARGON2_HASH_LEN,
    salt_len=ARGON2_SALT_LEN
)

def hashear_password(password: str) -> str:
    """
    Genera hash Argon2id de una contraseña
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        str: Hash de la contraseña
    """
    return ph.hash(password)

def verificar_password(password_hash: str, password: str) -> bool:
    """
    Verifica una contraseña contra su hash usando comparación segura
    
    Args:
        password_hash: Hash almacenado
        password: Contraseña a verificar
    
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