"""
Configuración centralizada de logging
"""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

def configurar_logging(
    nivel: str = "INFO",
    log_dir: str = "logs",
    nombre_aplicacion: str = "servidor"
):
    """
    Configura el sistema de logging
    
    Args:
        nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directorio para los logs
        nombre_aplicacion: Nombre de la aplicación (servidor/cliente)
    """
    # Crear directorio de logs
    Path(log_dir).mkdir(exist_ok=True)
    
    # Configurar nivel
    nivel_logging = getattr(logging, nivel.upper(), logging.INFO)
    
    # Formato detallado
    formato = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ════════════════════════════════════════════════════════
    # HANDLER 1: Archivo general (todos los logs)
    # ════════════════════════════════════════════════════════
    
    archivo_general = Path(log_dir) / f"{nombre_aplicacion}.log"
    handler_general = logging.handlers.RotatingFileHandler(
        archivo_general,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    handler_general.setLevel(nivel_logging)
    handler_general.setFormatter(formato)
    
    # ════════════════════════════════════════════════════════
    # HANDLER 2: Archivo de seguridad (solo warnings y errors)
    # ════════════════════════════════════════════════════════
    
    archivo_seguridad = Path(log_dir) / "seguridad.log"
    handler_seguridad = logging.handlers.RotatingFileHandler(
        archivo_seguridad,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    handler_seguridad.setLevel(logging.WARNING)
    handler_seguridad.setFormatter(formato)
    
    # ════════════════════════════════════════════════════════
    # HANDLER 3: Archivo de transacciones (solo info de transacciones)
    # ════════════════════════════════════════════════════════
    
    archivo_transacciones = Path(log_dir) / "transacciones.log"
    handler_transacciones = logging.FileHandler(
        archivo_transacciones,
        encoding='utf-8'
    )
    handler_transacciones.setLevel(logging.INFO)
    
    # Formato especial para transacciones
    formato_tx = logging.Formatter(
        fmt='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler_transacciones.setFormatter(formato_tx)
    
    # Filtro: solo logs de transacciones
    class FiltroTransacciones(logging.Filter):
        def filter(self, record):
            return 'transaccion' in record.getMessage().lower()
    
    handler_transacciones.addFilter(FiltroTransacciones())
    
    # ════════════════════════════════════════════════════════
    # HANDLER 4: Consola (stdout)
    # ════════════════════════════════════════════════════════
    
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(nivel_logging)
    handler_consola.setFormatter(formato)
    
    # ════════════════════════════════════════════════════════
    # CONFIGURAR ROOT LOGGER
    # ════════════════════════════════════════════════════════
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capturar todo, filtrar en handlers
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Añadir handlers
    root_logger.addHandler(handler_general)
    root_logger.addHandler(handler_seguridad)
    root_logger.addHandler(handler_transacciones)
    root_logger.addHandler(handler_consola)
    
    logging.info(" Sistema de logging configurado")
    logging.info(f" Logs en: {Path(log_dir).absolute()}")


def log_evento_seguridad(
    tipo: str,
    descripcion: str,
    origen: str = None,
    datos_adicionales: dict = None
):
    """
    Registra un evento de seguridad
    
    Args:
        tipo: Tipo de evento (REPLAY_ATTACK, MAC_INVALIDO, LOGIN_FALLIDO, etc.)
        descripcion: Descripción del evento
        origen: IP o identificador del origen
        datos_adicionales: Información adicional
    """
    logger = logging.getLogger("SEGURIDAD")
    
    mensaje = f"[{tipo}]"
    if origen:
        mensaje += f" [{origen}]"
    mensaje += f" {descripcion}"
    
    if datos_adicionales:
        mensaje += f" | Datos: {datos_adicionales}"
    
    logger.warning(mensaje)


def log_transaccion(
    username: str,
    cuenta_origen: str,
    cuenta_destino: str,
    cantidad: float,
    tx_id: int = None,
    mac_verificado: bool = True
):
    """
    Registra una transacción
    
    Args:
        username: Usuario
        cuenta_origen: Cuenta origen
        cuenta_destino: Cuenta destino
        cantidad: Cantidad transferida
        tx_id: ID de transacción
        mac_verificado: Si el MAC fue verificado correctamente
    """
    logger = logging.getLogger("TRANSACCIONES")
    
    estado_mac = "✓ MAC_OK" if mac_verificado else "✗ MAC_FAIL"
    
    mensaje = (
        f"TRANSACCION "
        f"[ID:{tx_id or 'N/A'}] "
        f"[USER:{username}] "
        f"[ORIGEN:{cuenta_origen}] → "
        f"[DESTINO:{cuenta_destino}] "
        f"[CANTIDAD:{cantidad:.2f} EUR] "
        f"[{estado_mac}]"
    )
    
    logger.info(mensaje)