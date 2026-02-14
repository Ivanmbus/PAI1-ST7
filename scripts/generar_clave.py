# scripts/generar_clave.py
"""
Genera una clave compartida criptográficamente segura
"""
import secrets
import base64
from pathlib import Path

def generar_clave_compartida():
    """Genera una clave de 256 bits (32 bytes)"""
    clave = secrets.token_bytes(32)
    
    # Guardar en archivo binario
    key_path = Path("config/shared_key.key")
    key_path.parent.mkdir(exist_ok=True)
    key_path.write_bytes(clave)
    
    # También mostrar en base64 para .env
    clave_b64 = base64.b64encode(clave).decode()
    
    print("✅ Clave compartida generada exitosamente")
    print(f"📁 Guardada en: {key_path}")
    print(f"\n🔑 Para usar en .env, añade esta línea:")
    print(f"SHARED_KEY={clave_b64}")
    
    return clave

if __name__ == "__main__":
    generar_clave_compartida()