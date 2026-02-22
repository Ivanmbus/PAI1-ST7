"""
Script para inicializar la base de datos
Crea las tablas necesarias ejecutando init_db.sql
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from server.database import DatabaseManager
from common.config import Config

def main():
    """Inicializa la base de datos"""
    print("🔧 Inicializando base de datos...")
    print(f"📁 Ruta: {Config.DB_PATH}")
    
    try:
        # Crear instancia de DatabaseManager (automáticamente inicializa la BD)
        db = DatabaseManager(Config.DB_PATH)
        print("✅ Base de datos inicializada correctamente")
        print(f"✓ Tablas creadas: usuarios, transacciones, nonces")
        
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())