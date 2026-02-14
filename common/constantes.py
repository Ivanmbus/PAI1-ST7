# common/constantes.py
"""
Constantes criptográficas del sistema
"""

# Tamaños
MAC_SIZE = 32  # bytes (HMAC-SHA256 produce 32 bytes)
NONCE_SIZE = 32  # bytes (256 bits)
KEY_SIZE = 32  # bytes (256 bits para HMAC)

# Algoritmos
HASH_ALGORITHM = "sha256"
MAC_ALGORITHM = "HMAC-SHA256"
PASSWORD_HASHER = "Argon2id"

# Argon2 parámetros
ARGON2_TIME_COST = 3  # iteraciones
ARGON2_MEMORY_COST = 65536  # 64 MB
ARGON2_PARALLELISM = 4  # hilos
ARGON2_HASH_LEN = 32  # bytes
ARGON2_SALT_LEN = 16  # bytes

# Configuración de red
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000
BUFFER_SIZE = 4096

# Mensajes
ENCODING = "utf-8"