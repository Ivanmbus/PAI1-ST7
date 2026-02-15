# servidor/servidor.py
"""
Servidor principal - Maneja UNA petición por conexión
OPCIÓN 1: Cierra después de cada respuesta
"""
import socket
import threading
import logging
import json
import signal
import sys
from typing import Optional

from server.database import DatabaseManager
from server.crypto_server import verificar_mensaje_completo, MensajeInvalido
from server.autenticacion import Autenticacion
from server.transacciones import GestorTransacciones
from common.config import Config
from common.protocolo import Mensaje

logger = logging.getLogger(__name__)

class ServidorBancario:
    """Servidor bancario - Una petición por conexión"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or Config.SERVER_HOST
        self.port = port or Config.SERVER_PORT
        
        # Base de datos
        self.db = DatabaseManager(Config.DB_PATH)
        
        # Clave compartida para MAC
        self.clave_compartida = Config.get_shared_key()
        
        # Gestores
        self.autenticacion = Autenticacion(self.db)
        self.transacciones = GestorTransacciones(self.db)
        
        # Socket
        self.socket_servidor: Optional[socket.socket] = None
        self.activo = False
        
        # Registrar manejador de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Manejador de señales (Ctrl+C, Ctrl+Break)"""
        print("\n")
        logger.info("[*] Señal de interrupcion recibida")
        self.detener()
        sys.exit(0)
    
    def iniciar(self):
        """Inicia el servidor"""
        try:
            # Crear socket
            self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Configurar timeout
            self.socket_servidor.settimeout(1.0)
            
            # Bind y listen
            self.socket_servidor.bind((self.host, self.port))
            self.socket_servidor.listen(5)
            
            self.activo = True
            
            logger.info("=" * 60)
            logger.info("")
            logger.info(f"   SERVIDOR INICIADO EN {self.host}:{self.port}")
            logger.info("")
            logger.info("=" * 60)
            logger.info("[OK] Clave compartida cargada correctamente")
            logger.info("[OK] Base de datos inicializada")
            logger.info("[OK] Modo: UNA PETICION POR CONEXION")
            logger.info("[*] Esperando conexiones de clientes...")
            logger.info("[*] Presiona Ctrl+C para detener\n")
            
            # Aceptar conexiones
            self._aceptar_conexiones()
            
        except Exception as e:
            logger.error(f"[ERROR] Error al iniciar servidor: {e}")
            raise
    
    def _aceptar_conexiones(self):
        """Acepta conexiones entrantes (loop principal)"""
        contador_conexiones = 0
        
        while self.activo:
            try:
                # Aceptar conexión
                conn, addr = self.socket_servidor.accept()
                contador_conexiones += 1
                logger.info(f"[IN] Conexion #{contador_conexiones} desde {addr}")
                
                # Crear thread para manejar el cliente
                thread = threading.Thread(
                    target=self._manejar_cliente,
                    args=(conn, addr, contador_conexiones),
                    daemon=True
                )
                thread.start()
                
            except socket.timeout:
                continue
                
            except KeyboardInterrupt:
                logger.info("\n[WARNING] Interrupcion del teclado")
                break
                
            except OSError as e:
                if not self.activo:
                    break
                logger.error(f"[ERROR] Error en socket: {e}")
                
            except Exception as e:
                if self.activo:
                    logger.error(f"[ERROR] Error aceptando conexion: {e}")
    
    def _manejar_cliente(self, conn: socket.socket, addr: tuple, num_conn: int):
        """
        Maneja UNA petición y cierra la conexión
        ✅ OPCIÓN 1: Procesa UN mensaje y cierra
        """
        try:
            # Recibir datos
            datos = conn.recv(4096)
            
            if not datos:
                logger.warning(f"[WARNING] {addr} - Conexion cerrada sin datos")
                return
            
            logger.debug(f"[*] #{num_conn} Recibidos {len(datos)} bytes")
            
            # Desempaquetar mensaje
            try:
                mensaje_bytes, mac, nonce = Mensaje.desempaquetar(datos)
            except Exception as e:
                logger.error(f"[ERROR] {addr} - Error al desempaquetar: {e}")
                self._enviar_error(conn, "Mensaje malformado")
                return
            
            # Validar integridad (MAC + NONCE)
            try:
                verificar_mensaje_completo(
                    db_manager=self.db,
                    clave=self.clave_compartida,
                    mensaje=mensaje_bytes,
                    nonce=nonce,
                    mac_recibido=mac
                )
            except MensajeInvalido as e:
                logger.warning(f"[ALERT] {addr} - Mensaje rechazado: {e}")
                self._enviar_error(conn, str(e))
                return
            
            # Parsear mensaje
            mensaje = Mensaje.desde_json(mensaje_bytes)
            logger.info(f"[OK] #{num_conn} - Tipo: {mensaje.tipo}")
            
            # Procesar según tipo
            if mensaje.tipo == Mensaje.REGISTRO:
                self._procesar_registro(conn, mensaje, addr)
            
            elif mensaje.tipo == Mensaje.LOGIN:
                self._procesar_login(conn, mensaje, addr)
            
            elif mensaje.tipo == Mensaje.TRANSACCION:
                self._procesar_transaccion(conn, mensaje, addr)
            
            else:
                logger.warning(f"[WARNING] {addr} - Tipo desconocido: {mensaje.tipo}")
                self._enviar_error(conn, "Tipo de mensaje no soportado")
        
        except Exception as e:
            logger.error(f"[ERROR] {addr} - Error: {e}", exc_info=True)
        
        finally:
            # ✅ OPCIÓN 1: SIEMPRE cerrar después de responder
            conn.close()
            logger.debug(f"[CLOSE] #{num_conn} - Conexion cerrada")
    
    def _procesar_registro(self, conn, mensaje, addr):
        username = mensaje.datos.get("username")
        password = mensaje.datos.get("password")
        
        if not username or not password:
            self._enviar_error(conn, "Faltan datos de registro")
            return
        
        exito, msg = self.autenticacion.registrar(username, password)
        
        if exito:
            self._enviar_ok(conn, msg)
        else:
            self._enviar_error(conn, msg)
    
    def _procesar_login(self, conn, mensaje, addr):
        username = mensaje.datos.get("username")
        password = mensaje.datos.get("password")
        
        if not username or not password:
            self._enviar_error(conn, "Faltan credenciales")
            return
        
        exito, msg = self.autenticacion.login(username, password)
        
        if exito:
            self._enviar_ok(conn, msg)
        else:
            self._enviar_error(conn, msg)
    
    def _procesar_transaccion(self, conn, mensaje, addr):
        username = mensaje.datos.get("username")
        cuenta_origen = mensaje.datos.get("cuenta_origen")
        cuenta_destino = mensaje.datos.get("cuenta_destino")
        cantidad = mensaje.datos.get("cantidad")
        
        if not all([username, cuenta_origen, cuenta_destino, cantidad]):
            self._enviar_error(conn, "Faltan datos de la transaccion")
            return
        
        exito, msg = self.transacciones.procesar_transferencia(
            username, cuenta_origen, cuenta_destino, cantidad
        )
        
        if exito:
            self._enviar_ok(conn, msg)
        else:
            self._enviar_error(conn, msg)
    
    def _enviar_ok(self, conn, mensaje, datos=None):
        respuesta = {
            "status": "ok",
            "mensaje": mensaje,
            "datos": datos or {}
        }
        self._enviar_respuesta(conn, respuesta)
    
    def _enviar_error(self, conn, mensaje):
        respuesta = {
            "status": "error",
            "mensaje": mensaje
        }
        self._enviar_respuesta(conn, respuesta)
    
    def _enviar_respuesta(self, conn, respuesta):
        try:
            datos = json.dumps(respuesta).encode('utf-8')
            conn.sendall(datos)
        except Exception as e:
            logger.error(f"[ERROR] Error enviando respuesta: {e}")
    
    def detener(self):
        if not self.activo:
            return
        
        logger.info("[STOP] Deteniendo servidor...")
        self.activo = False
        
        if self.socket_servidor:
            try:
                self.socket_servidor.close()
            except Exception as e:
                logger.error(f"[ERROR] Error cerrando socket: {e}")
        
        logger.info("[OK] Servidor detenido correctamente")


def main():
    import sys
    from pathlib import Path
    
    Path("logs").mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/servidor.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    servidor = ServidorBancario()
    
    try:
        servidor.iniciar()
    except KeyboardInterrupt:
        print("\n")
        logger.info("[*] Servidor interrumpido")
        servidor.detener()
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()