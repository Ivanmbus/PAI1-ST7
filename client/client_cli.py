# cliente/cliente_cli.py
"""
Interfaz de línea de comandos del cliente
"""
import json
import logging
from getpass import getpass
from typing import Optional

from .communicacion import ClienteSocket
from .crypto_client import preparar_mensaje_seguro
from common.config import Config
from common.protocolo import Mensaje

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ClienteCLI:
    """Cliente de línea de comandos"""
    
    def __init__(self):
        self.socket_cliente = ClienteSocket(Config.SERVER_HOST, Config.SERVER_PORT)
        self.clave_compartida = Config.get_shared_key()
        self.username_actual: Optional[str] = None
        self.sesion_activa = False
    
    def limpiar_pantalla(self):
        """Limpia la pantalla (multiplataforma)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_banner(self):
        """Muestra el banner inicial"""
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + "   SISTEMA BANCARIO SEGURO - CLIENTE".center(58) + "║")
        print("║" + "   PAI1-INTEGRIDOS".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "═" * 58 + "╝")
        print()
    
    def enviar_mensaje(self, mensaje: Mensaje) -> Optional[dict]:
        """
        Envía un mensaje protegido al servidor
        
        Args:
            mensaje: Mensaje a enviar
        
        Returns:
            dict: Respuesta del servidor o None si hay error
        """
        # Empaquetar mensaje con MAC y NONCE
        paquete = mensaje.empaquetar(self.clave_compartida)
        
        # Enviar y recibir respuesta
        respuesta = self.socket_cliente.enviar_y_recibir(paquete)
        
        return respuesta
    
    # ════════════════════════════════════════════════════════
    # MENÚ PRINCIPAL (SIN LOGIN)
    # ════════════════════════════════════════════════════════
    
    def menu_principal(self):
        """Menú principal (usuario no logueado)"""
        while True:
            print("\n" + "─" * 60)
            print("   MENÚ PRINCIPAL")
            print("─" * 60)
            print("[1] Registro de nuevo usuario")
            print("[2] Iniciar sesión (Login)")
            print("[3] Salir")
            print("─" * 60)
            
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion == "1":
                self.registrar_usuario()
            elif opcion == "2":
                if self.iniciar_sesion():
                    self.menu_sesion()
            elif opcion == "3":
                print("\n ¡Hasta luego!")
                break
            else:
                print("[ERROR] Opción inválida")
    
    # ════════════════════════════════════════════════════════
    # REGISTRO
    # ════════════════════════════════════════════════════════
    
    def registrar_usuario(self):
        """Proceso de registro de nuevo usuario"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + "   REGISTRO DE NUEVO USUARIO".center(58) + "║")
        print("╚" + "═" * 58 + "╝")
        print()
        
        username = input("Nombre de usuario: ").strip()
        if not username:
            print("[ERROR] El nombre de usuario no puede estar vacío")
            return
        
        password = getpass("Contraseña: ")
        if not password:
            print("[ERROR] La contraseña no puede estar vacía")
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
        
        print("\n[LOCK] Preparando mensaje seguro...")
        print("   ├─ Generando NONCE...")
        print("   ├─ Calculando MAC...")
        print("   └─ Enviando al servidor...")
        
        # Enviar al servidor
        respuesta = self.enviar_mensaje(mensaje)
        
        if not respuesta:
            print("[ERROR] Error de comunicación con el servidor")
            return
        
        # Procesar respuesta
        if respuesta.get("status") == "ok":
            print(f"\n[OK] {respuesta.get('mensaje')}")
            print(f"   Usuario '{username}' registrado exitosamente")
        else:
            print(f"\n[ERROR] {respuesta.get('mensaje')}")
    
    # ════════════════════════════════════════════════════════
    # LOGIN
    # ════════════════════════════════════════════════════════
    
    def iniciar_sesion(self) -> bool:
        """
        Proceso de inicio de sesión
        
        Returns:
            bool: True si el login fue exitoso
        """
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + "   INICIAR SESIÓN".center(58) + "║")
        print("╚" + "═" * 58 + "╝")
        print()
        
        username = input("Nombre de usuario: ").strip()
        password = getpass("Contraseña: ")
        
        # Crear mensaje de login
        mensaje = Mensaje(
            tipo=Mensaje.LOGIN,
            datos={
                "username": username,
                "password": password
            }
        )
        
        print("\n[LOCK] Autenticando...")
        
        # Enviar al servidor
        respuesta = self.enviar_mensaje(mensaje)
        
        if not respuesta:
            print("[ERROR] Error de comunicación con el servidor")
            return False
        
        # Procesar respuesta
        if respuesta.get("status") == "ok":
            self.username_actual = username
            self.sesion_activa = True
            print(f"\n[OK] {respuesta.get('mensaje')}")
            print(f"   Bienvenido, {username}!")
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
            print("\n" + "─" * 60)
            print(f"   SESIÓN ACTIVA - Usuario: {self.username_actual}")
            print("─" * 60)
            print("[1] Realizar transferencia")
            print("[2] Ver mis transacciones")
            print("[3] Cerrar sesión")
            print("─" * 60)
            
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion == "1":
                self.realizar_transferencia()
            elif opcion == "2":
                self.ver_transacciones()
            elif opcion == "3":
                self.cerrar_sesion()
            else:
                print("[ERROR] Opción inválida")
    
    # ════════════════════════════════════════════════════════
    # TRANSACCIONES
    # ════════════════════════════════════════════════════════
    
    def realizar_transferencia(self):
        """Proceso de transferencia bancaria"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + "   NUEVA TRANSFERENCIA".center(58) + "║")
        print("╚" + "═" * 58 + "╝")
        print()
        
        cuenta_origen = input("Cuenta origen (IBAN): ").strip()
        if not cuenta_origen:
            print("[ERROR] La cuenta origen no puede estar vacía")
            return
        
        cuenta_destino = input("Cuenta destino (IBAN): ").strip()
        if not cuenta_destino:
            print("[ERROR] La cuenta destino no puede estar vacía")
            return
        
        try:
            cantidad = float(input("Cantidad (EUR): ").strip())
            if cantidad <= 0:
                print("[ERROR] La cantidad debe ser mayor a 0")
                return
        except ValueError:
            print("[ERROR] Cantidad inválida")
            return
        
        # Confirmación
        print("\n" + "─" * 60)
        print("   CONFIRMAR TRANSFERENCIA")
        print("─" * 60)
        print(f"   Origen:   {cuenta_origen}")
        print(f"   Destino:  {cuenta_destino}")
        print(f"   Cantidad: {cantidad:.2f} EUR")
        print("─" * 60)
        
        confirmar = input("\n¿Confirmar transferencia? (s/n): ").strip().lower()
        if confirmar != 's':
            print("[ERROR] Transferencia cancelada")
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
        
        print("\n[LOCK] Procesando transferencia segura...")
        print("   ├─ Generando NONCE único...")
        print("   ├─ Calculando MAC de transacción...")
        print("   └─ Enviando al servidor...")
        
        # Enviar al servidor
        respuesta = self.enviar_mensaje(mensaje)
        
        if not respuesta:
            print("[ERROR] Error de comunicación con el servidor")
            return
        
        # Procesar respuesta
        if respuesta.get("status") == "ok":
            print(f"\n[OK] {respuesta.get('mensaje')}")
            print(f"   Transferencia de {cantidad:.2f} EUR completada")
            print("   ✓ Integridad verificada (MAC válido)")
        else:
            print(f"\n[ERROR] {respuesta.get('mensaje')}")
    
    def ver_transacciones(self):
        """Ver transacciones del usuario"""
        print("\n Funcionalidad en desarrollo...")
        print("   (Implementar en Fase 6)")
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        print(f"\n Cerrando sesión de {self.username_actual}...")
        self.username_actual = None
        self.sesion_activa = False
        print("[OK] Sesión cerrada")
    
    # ════════════════════════════════════════════════════════
    # INICIAR CLIENTE
    # ════════════════════════════════════════════════════════
    
    def iniciar(self):
        """Inicia el cliente"""
        self.limpiar_pantalla()
        self.mostrar_banner()
        
        # Conectar al servidor
        if not self.socket_cliente.conectar():
            print("[Error] No se pudo conectar al servidor")
            print("   Asegúrate de que el servidor esté ejecutándose")
            return
        
        try:
            # Mostrar menú principal
            self.menu_principal()
        finally:
            # Desconectar al salir
            self.socket_cliente.desconectar()


# ════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════

def main():
    """Función principal"""
    cliente = ClienteCLI()
    cliente.iniciar()


if __name__ == "__main__":
    main()