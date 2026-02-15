import socket
import json
import logging
from typing import Optional, Tuple

from common.constantes import DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE

logger = logging.getLogger(__name__)

class ClienteSocket:
    """Gestiona la conexión socket con el servidor"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
    
    def conectar(self) -> bool:
        """
        Establece conexión con el servidor
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logger.info(f"[OK]Conectado al servidor {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            logger.error(f"[ERROR] No se pudo conectar a {self.host}:{self.port}")
            logger.error("   ¿Está el servidor ejecutándose?")
            return False
        except Exception as e:
            logger.error(f"[ERROR] Error al conectar: {e}")
            return False
    
    def enviar(self, datos: bytes) -> bool:
        """
        Envía datos al servidor
        
        Args:
            datos: Bytes a enviar (paquete completo)
        
        Returns:
            bool: True si el envío fue exitoso
        """
        if not self.socket:
            logger.error("[ERROR] Socket no conectado")
            return False
        
        try:
            self.socket.sendall(datos)
            logger.debug(f" Enviados {len(datos)} bytes")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Error al enviar: {e}")
            return False
    
    def recibir(self) -> Optional[bytes]:
        """
        Recibe datos del servidor
        
        Returns:
            bytes: Datos recibidos o None si hay error
        """
        if not self.socket:
            logger.error("[ERROR] Socket no conectado")
            return None
        
        try:
            datos = self.socket.recv(BUFFER_SIZE)
            if not datos:
                logger.warning("[WARNING]  Servidor cerró la conexión")
                return None
            
            logger.debug(f" Recibidos {len(datos)} bytes")
            return datos
        except Exception as e:
            logger.error(f"[ERROR] Error al recibir: {e}")
            return None
    
    def enviar_y_recibir(self, datos: bytes) -> Optional[dict]:
        """
        Envía datos y espera respuesta del servidor
        
        Args:
            datos: Paquete a enviar
        
        Returns:
            dict: Respuesta parseada del servidor
        """
        if not self.enviar(datos):
            return None
        
        respuesta_bytes = self.recibir()
        if not respuesta_bytes:
            return None
        
        try:
            respuesta = json.loads(respuesta_bytes.decode('utf-8'))
            return respuesta
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] Error parseando respuesta: {e}")
            return None
    
    def desconectar(self):
        """Cierra la conexión con el servidor"""
        if self.socket:
            try:
                self.socket.close()
                logger.info("🔌 Desconectado del servidor")
            except Exception as e:
                logger.error(f"[ERROR] Error al desconectar: {e}")
            finally:
                self.socket = None
    
    def __enter__(self):
        """Context manager: entrada"""
        self.conectar()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: salida"""
        self.desconectar()