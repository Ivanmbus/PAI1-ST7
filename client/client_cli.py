# cliente/cliente_cli.py
"""
Interfaz de línea de comandos del cliente
OPCIÓN 1: Reconexión automática por mensaje
"""
import json
import logging
from getpass import getpass
from typing import Optional

from client.communicacion import ClienteSocket
from common.config import Config
from common.protocolo import Mensaje

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ClienteCLI:
    """Cliente de línea de comandos con reconexión automática"""
    
    def __init__(self):
        # ✅ NO mantener socket abierto, solo guardar config
        self.host = Config.SERVER_HOST
        self.port = Config.SERVER_PORT
        self.clave_compartida = Config.get_shared_key()
        
        # Estado de sesión (solo local)
        self.username_actual: Optional[str] = None
        self.sesion_activa = False
    
    def limpiar_pantalla(self):
        """Limpia la pantalla (multiplataforma)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_banner(self):
        """Muestra el banner inicial"""
        print("=" * 60)
        print("")
        print("   SISTEMA BANCARIO SEGURO - CLIENTE".center(60))
        print("   PAI1-INTEGRIDOS".center(60))
        print("   (Reconexion automatica)".center(60))
        print("")
        print("=" * 60)
        print()
    
    def enviar_mensaje(self, mensaje: Mensaje) -> Optional[dict]:
        """
        Envía un mensaje protegido al servidor
        ✅ OPCIÓN 1: Crea nueva conexión para cada mensaje
        
        Args:
            mensaje: Mensaje a enviar
        
        Returns:
            dict: Respuesta del servidor o None si hay error
        """
        try:
            # ✅ Crear nueva conexión temporal
            socket_temp = ClienteSocket(self.host, self.port)
            
            logger.debug(f"[*] Conectando al servidor...")
            if not socket_temp.conectar():
                logger.error("No se pudo conectar al servidor")
                return None
            
            logger.debug(f"[OK] Conectado")
            
            # Empaquetar mensaje con MAC y NONCE
            paquete = mensaje.empaquetar(self.clave_compartida)
            
            # Enviar y recibir respuesta
            logger.debug(f"[*] Enviando mensaje...")
            respuesta = socket_temp.enviar_y_recibir(paquete)
            
            # ✅ Cerrar conexión inmediatamente
            socket_temp.desconectar()
            logger.debug(f"[OK] Desconectado")
            
            return respuesta
            
        except Exception as e:
            logger.error(f"Error en comunicacion: {e}")
            return None
    
    # ════════════════════════════════════════════════════════
    # MENÚ PRINCIPAL (SIN LOGIN)
    # ════════════════════════════════════════════════════════
    
    def menu_principal(self):
        """Menú principal (usuario no logueado)"""
        while True:
            print("\n" + "-" * 60)
            print("   MENU PRINCIPAL")
            print("-" * 60)
            print("[1] Registro de nuevo usuario")
            print("[2] Iniciar sesion (Login)")
            print("[3] Salir")
            print("-" * 60)
            
            opcion = input("\nSeleccione una opcion: ").strip()
            
            if opcion == "1":
                self.registrar_usuario()
            elif opcion == "2":
                if self.iniciar_sesion():
                    self.menu_sesion()
            elif opcion == "3":
                print("\n[*] Hasta luego!")
                break
            else:
                print("[ERROR] Opcion invalida")
    
    # ════════════════════════════════════════════════════════
    # REGISTRO
    # ════════════════════════════════════════════════════════
    
    def registrar_usuario(self):
        """Proceso de registro de nuevo usuario"""
        print("\n" + "=" * 60)
        print("   REGISTRO DE NUEVO USUARIO".center(60))
        print("=" * 60)
        print()
        
        username = input("Nombre de usuario: ").strip()
        if not username:
            print("[ERROR] El nombre de usuario no puede estar vacio")
            return
        
        password = getpass("Contraseña: ")
        if not password:
            print("[ERROR] La contraseña no puede estar vacia")
            return
        
        password_confirm = getpass("Confirmar contraseña: ")
        if password != password_confirm:
            print("[ERROR] Las contraseñas no coinciden")
            return
        
        # Crear mensaje de registro
        mensaje = Mensaje(
            tipo=Mensaje.REGISTRO,
            datos={
                "username": username,
                "password": password
            }
        )
        if self.username_actual == "admin":
            print("\n[*] ADMIN: Preparando mensaje seguro...")
            print("   |-- Generando NONCE...")
            print("   |-- Calculando MAC...")
            print("   |-- Conectando y enviando al servidor...")
        
        # ✅ Enviar al servidor (reconecta automáticamente)
        respuesta = self.enviar_mensaje(mensaje)
        
        if not respuesta:
            print("[ERROR] Error de comunicacion con el servidor")
            return
        
        # Procesar respuesta
        if respuesta.get("status") == "ok":
            print(f"\n[OK] {respuesta.get('mensaje')}")
            print(f"    Usuario '{username}' registrado exitosamente")
        else:
            print(f"\n[ERROR] {respuesta.get('mensaje')}")
    
    # ════════════════════════════════════════════════════════
    # LOGIN
    # ════════════════════════════════════════════════════════
    
    def iniciar_sesion(self) -> bool:
        """
        Proceso de inicio de sesión
        El SERVIDOR maneja todos los intentos y bloqueos
        """
        print("\n" + "=" * 60)
        print("   INICIAR SESION".center(60))
        print("=" * 60)
        print()
        
        username = input("Nombre de usuario: ").strip()
        if not username:
            print("[ERROR] El nombre de usuario no puede estar vacio")
            return False
        
        password = getpass("Contraseña: ")
        if not password:
            print("[ERROR] La contraseña no puede estar vacia")
            return False
        
        # Crear mensaje de login
        mensaje = Mensaje(
            tipo=Mensaje.LOGIN,
            datos={
                "username": username,
                "password": password
            }
        )
        
        print("\n[*] Autenticando...")
        
        # Enviar al servidor
        respuesta = self.enviar_mensaje(mensaje)
        
        if not respuesta:
            print("[ERROR] Error de comunicacion con el servidor")
            return False
        
        # Procesar respuesta
        if respuesta.get("status") == "ok":
            self.username_actual = username
            self.sesion_activa = True
            print(f"\n[OK] {respuesta.get('mensaje')}")
            print(f"    Bienvenido, {username}!")
            return True
        else:
            print(f"\n[ERROR] {respuesta.get('mensaje')}")
            return False
    # ════════════════════════════════════════════════════════
    # MENÚ DE SESIÓN (USUARIO LOGUEADO)
    # ════════════════════════════════════════════════════════
    
    def menu_sesion(self):
        """Menú para usuario con sesión activa"""
        while self.sesion_activa:
            print("\n" + "-" * 60)
            print(f"   SESION ACTIVA - Usuario: {self.username_actual}")
            print("-" * 60)
            print("[1] Realizar transferencia")
            print("[2] Cerrar sesion")
            print("-" * 60)
            
            opcion = input("\nSeleccione una opcion: ").strip()
            
            if opcion == "1":
                self.realizar_transferencia()
            elif opcion == "2":
                self.cerrar_sesion()
            else:
                print("[ERROR] Opcion invalida")
    
    # ════════════════════════════════════════════════════════
    # TRANSACCIONES
    # ════════════════════════════════════════════════════════
    
    def realizar_transferencia(self):
        """Proceso de transferencia bancaria"""
        print("\n" + "=" * 60)
        print("   NUEVA TRANSFERENCIA".center(60))
        print("=" * 60)
        print()
        
        cuenta_origen = input("Cuenta origen (IBAN): ").strip()
        if not cuenta_origen:
            print("[ERROR] La cuenta origen no puede estar vacia")
            return
        
        cuenta_destino = input("Cuenta destino (IBAN): ").strip()
        if not cuenta_destino:
            print("[ERROR] La cuenta destino no puede estar vacia")
            return
        
        try:
            cantidad = float(input("Cantidad (EUR): ").strip())
            if cantidad <= 0:
                print("[ERROR] La cantidad debe ser mayor a 0")
                return
        except ValueError:
            print("[ERROR] Cantidad invalida")
            return
        
        # Confirmación
        print("\n" + "-" * 60)
        print("   CONFIRMAR TRANSFERENCIA")
        print("-" * 60)
        print(f"   Origen:   {cuenta_origen}")
        print(f"   Destino:  {cuenta_destino}")
        print(f"   Cantidad: {cantidad:.2f} EUR")
        print("-" * 60)
        
        confirmar = input("\n¿Confirmar transferencia? (s/n): ").strip().lower()
        if confirmar != 's':
            print("[*] Transferencia cancelada")
            return
        
        # Crear mensaje de transacción
        mensaje = Mensaje(
            tipo=Mensaje.TRANSACCION,
            datos={
                "username": self.username_actual,
                "cuenta_origen": cuenta_origen,
                "cuenta_destino": cuenta_destino,
                "cantidad": cantidad
            }
        )
        if self.username_actual == "admin":
            print("\n[*] ADMIN: Procesando transferencia segura...")
            print("   |-- Generando NONCE unico...")
            print("   |-- Calculando MAC de transaccion...")
            print("   |-- Conectando y enviando al servidor...")
        
        # ✅ Enviar al servidor (reconecta automáticamente)
        respuesta = self.enviar_mensaje(mensaje)
        
        if not respuesta:
            print("[ERROR] Error de comunicacion con el servidor")
            return
        
        # Procesar respuesta
        if respuesta.get("status") == "ok":
            if self.username_actual == "admin":   
                print(f"\n[OK] ADMIN: {respuesta.get('mensaje')}")
            print(f"    Transferencia de {cantidad:.2f} EUR completada")
            print("    [OK] Integridad verificada (MAC valido)")
        else:
            print(f"\n[ERROR] {respuesta.get('mensaje')}")
    

    
    def cerrar_sesion(self):
        """Cierra la sesión actual (solo local, no envía al servidor)"""
        print(f"\n[*] Cerrando sesion de {self.username_actual}...")
        
        # ✅ OPCIÓN 1: No enviar mensaje al servidor, solo cerrar localmente
        self.username_actual = None
        self.sesion_activa = False
        
        print("[OK] Sesion cerrada")
    
    # ════════════════════════════════════════════════════════
    # INICIAR CLIENTE
    # ════════════════════════════════════════════════════════
    
    def iniciar(self):
        """Inicia el cliente"""
        self.limpiar_pantalla()
        self.mostrar_banner()
        
        # ✅ OPCIÓN 1: NO conectar al inicio
        # Cada mensaje creará su propia conexión
        
        print(f"[*] Configurado para: {self.host}:{self.port}")
        print("[OK] Reconexion automatica habilitada\n")
        
        try:
            # Mostrar menú principal
            self.menu_principal()
        except Exception as e:
            logger.error(f"Error: {e}")


# ════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════

def main():
    """Función principal"""
    cliente = ClienteCLI()
    cliente.iniciar()


if __name__ == "__main__":
    main()