# common/protocolo.py
"""
Protocolo de comunicación cliente-servidor
"""
import json
import base64
from typing import Dict, Any, Tuple
from crypto__utils import calcular_mac, generar_nonce
from .constantes import ENCODING

class Mensaje:
    """Representa un mensaje del protocolo"""
    
    # Tipos de mensaje
    REGISTRO = "registro"
    LOGIN = "login"
    TRANSACCION = "transaccion"
    LOGOUT = "logout"
    RESPUESTA = "respuesta"
    
    def __init__(self, tipo: str, datos: Dict[str, Any]):
        self.tipo = tipo
        self.datos = datos
    
    def serializar(self, clave: bytes) -> Tuple[bytes, bytes, bytes]:
        """
        Serializa el mensaje con protección de integridad
        
        Args:
            clave: Clave compartida para MAC
        
        Returns:
            Tuple[bytes, bytes, bytes]: (mensaje_json, mac, nonce)
        """
        # Crear estructura del mensaje
        mensaje_dict = {
            "tipo": self.tipo,
            "datos": self.datos
        }
        
        # Serializar a JSON
        mensaje_json = json.dumps(mensaje_dict).encode(ENCODING)
        
        # Generar NONCE
        nonce = generar_nonce()
        
        # Calcular MAC
        mac = calcular_mac(clave, mensaje_json, nonce)
        
        return mensaje_json, mac, nonce
    
    def empaquetar(self, clave: bytes) -> bytes:
        """
        Empaqueta el mensaje completo para envío por socket
        
        Formato: [tamaño_mensaje][mensaje][tamaño_mac][mac][tamaño_nonce][nonce]
        """
        mensaje_json, mac, nonce = self.serializar(clave)
        
        # Crear paquete con tamaños
        paquete = {
            "mensaje": base64.b64encode(mensaje_json).decode('ascii'),
            "mac": base64.b64encode(mac).decode('ascii'),
            "nonce": base64.b64encode(nonce).decode('ascii')
        }
        
        return json.dumps(paquete).encode(ENCODING)
    
    @staticmethod
    def desempaquetar(paquete_bytes: bytes) -> Tuple[bytes, bytes, bytes]:
        """
        Desempaqueta un mensaje recibido
        
        Returns:
            Tuple[bytes, bytes, bytes]: (mensaje, mac, nonce)
        """
        paquete = json.loads(paquete_bytes.decode(ENCODING))
        
        mensaje = base64.b64decode(paquete["mensaje"])
        mac = base64.b64decode(paquete["mac"])
        nonce = base64.b64decode(paquete["nonce"])
        
        return mensaje, mac, nonce
    
    @staticmethod
    def desde_json(mensaje_json: bytes) -> 'Mensaje':
        """Crea un Mensaje desde JSON"""
        mensaje_dict = json.loads(mensaje_json.decode(ENCODING))
        return Mensaje(mensaje_dict["tipo"], mensaje_dict["datos"])

class MensajeRespuesta:
    """Mensaje de respuesta del servidor"""
    
    def __init__(self, status: str, mensaje: str, datos: Dict[str, Any] = None):
        self.status = status  # "ok" o "error"
        self.mensaje = mensaje
        self.datos = datos or {}
    
    def a_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "mensaje": self.mensaje,
            "datos": self.datos
        }
    
    def empaquetar(self) -> bytes:
        """Empaqueta la respuesta (sin MAC para simplificar)"""
        return json.dumps(self.a_dict()).encode(ENCODING)