import logging
from typing import Tuple

from server.database import DatabaseManager

logger = logging.getLogger(__name__)

class GestorTransacciones:
    """Gestiona las transacciones bancarias"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def procesar_transferencia(
        self,
        username: str,
        cuenta_origen: str,
        cuenta_destino: str,
        cantidad: float
    ) -> Tuple[bool, str]:
        """
        Procesa una transferencia bancaria
        
        Args:
            username: Usuario que realiza la transferencia
            cuenta_origen: IBAN origen
            cuenta_destino: IBAN destino
            cantidad: Cantidad a transferir
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        
        Nota:
            Según el enunciado, NO se validan cuentas ni cantidades.
            Solo se registra la transacción.
        """
        try:
            # Registrar transacción en BD
            tx_id = self.db.registrar_transaccion(
                username=username,
                cuenta_origen=cuenta_origen,
                cuenta_destino=cuenta_destino,
                cantidad=cantidad,
                mac_verificado=True  # Ya se verificó antes de llegar aquí
            )
            
            logger.info(
                f"[OK] Transacción registrada (ID: {tx_id}): "
                f"{username} → {cantidad:.2f} EUR "
                f"({cuenta_origen} → {cuenta_destino})"
            )
            
            return True, f"Transferencia completada (ID: {tx_id})"
            
        except Exception as e:
            logger.error(f"[ERROR] Error al procesar transferencia: {e}")
            return False, "Error al procesar la transferencia"
    
    def obtener_transacciones(self, username: str) -> list:
        """
        Obtiene las transacciones de un usuario
        
        Args:
            username: Usuario
        
        Returns:
            list: Lista de transacciones
        """
        try:
            transacciones = self.db.obtener_transacciones_usuario(username)
            logger.info(f"[OK] Consultadas {len(transacciones)} transacciones de {username}")
            return transacciones
        except Exception as e:
            logger.error(f"[ERROR] Error al obtener transacciones: {e}")
            return []