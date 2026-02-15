"""
Script para iniciar el servidor
"""
import sys
import logging
import signal
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Crear directorio de logs si no existe
Path("logs").mkdir(exist_ok=True)

from server.server import main, ServidorBancario

# Variable global para el servidor
servidor_global = None

def signal_handler(sig, frame):
    """Manejador de señales para cierre limpio"""
    print("\n")
    logging.info("[*] Señal de interrupcion recibida")
    if servidor_global:
        servidor_global.detener()
    sys.exit(0)

if __name__ == "__main__":
    # Registrar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)  # kill
    
    try:
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/servidor.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Crear servidor
        servidor_global = ServidorBancario()
        servidor_global.iniciar()
        
    except KeyboardInterrupt:
        print("\n")
        logging.info("[*] Servidor detenido por el usuario")
        if servidor_global:
            servidor_global.detener()
        sys.exit(0)
    except Exception as e:
        logging.error(f"[ERROR] Error fatal: {e}", exc_info=True)
        sys.exit(1)