# run_cliente.py
"""
Script para iniciar el cliente
"""
import sys
import logging
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from client.client_cli import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        logging.error(f"❌ Error fatal: {e}", exc_info=True)
        sys.exit(1)