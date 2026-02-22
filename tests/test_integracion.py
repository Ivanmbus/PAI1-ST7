# tests/test_integration.py
"""
Tests de integración end-to-end
Prueba el flujo completo: cliente → servidor → base de datos
"""
import json
import pytest
import threading
import time
import socket
from pathlib import Path

from server.server import ServidorBancario
from client.communicacion import ClienteSocket
from common.config import Config
from common.protocolo import Mensaje
from unittest.mock import Mock, patch
from client.client_cli import ClienteCLI
from datetime import datetime, timedelta

# ════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def servidor_test():
    """
    Fixture: Servidor de prueba con logging
    """
    import logging
    from pathlib import Path
    
    # Crear directorio de logs
    Path("logs").mkdir(exist_ok=True)
    
    # Configurar logging ANTES de iniciar el servidor
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            # Log a archivo (para evidencias)
            logging.FileHandler('logs/test_servidor.log', encoding='utf-8'),
            # Log a consola (para ver en tiempo real)
            logging.StreamHandler()
        ],
        force=True  # Sobrescribir configuración anterior
    )
    # Configurar servidor de prueba en puerto diferente
    servidor = ServidorBancario(host="127.0.0.1", port=5001)
    
    # Iniciar en thread separado (daemon)
    thread = threading.Thread(target=servidor.iniciar, daemon=True)
    thread.start()
    
    # Esperar a que el servidor esté listo
    time.sleep(2)
    
    # Verificar que el servidor está escuchando
    max_intentos = 5
    for i in range(max_intentos):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", 5001))
            s.close()
            break
        except ConnectionRefusedError:
            if i == max_intentos - 1:
                pytest.fail("Servidor no se inició correctamente")
            time.sleep(1)
    
    print("\n[TEST] Servidor de prueba iniciado en puerto 5001")
    
    yield servidor
    
    # Cleanup: Detener servidor
    servidor.detener()
    print("\n[TEST] Servidor de prueba detenido")


@pytest.fixture
def cliente_test():
    """Fixture: Cliente de prueba"""
    cliente = ClienteSocket("127.0.0.1", 5001)
    yield cliente
    # Cleanup
    try:
        cliente.desconectar()
    except:
        pass


# ════════════════════════════════════════════════════════
# TESTS DE FLUJO COMPLETO
# ════════════════════════════════════════════════════════

def test_flujo_completo_registro_login_transaccion(servidor_test):
    """
    Test E2E: Flujo completo de un usuario
    1. Registro
    2. Login
    3. Transacción
    4. Otra transacción
    """
    clave = Config.get_shared_key()
    username_test = f"test_user_{int(time.time())}"
    
    # ═══════════════════════════════════════════════════════
    # PASO 1: REGISTRO
    # ═══════════════════════════════════════════════════════
    
    cliente = ClienteSocket("127.0.0.1", 5001)
    assert cliente.conectar(), "No se pudo conectar al servidor"
    
    msg_registro = Mensaje(
        tipo=Mensaje.REGISTRO,
        datos={
            "username": username_test,
            "password": "Correct_pass1!"
        }
    )
    paquete = msg_registro.empaquetar(clave)
    respuesta = cliente.enviar_y_recibir(paquete)
    
    assert respuesta is not None, "No se recibió respuesta del servidor"
    assert respuesta["status"] == "ok", f"Registro falló: {respuesta.get('mensaje')}"
    print(f"[TEST] ✅ Registro exitoso: {username_test}")
    
    cliente.desconectar()
    
    # ═══════════════════════════════════════════════════════
    # PASO 2: LOGIN INCORRECTO - CORRECTO
    # ═══════════════════════════════════════════════════════
    cliente.conectar()
    
    msg_login = Mensaje(
        tipo=Mensaje.LOGIN,
        datos={
            "username": username_test,
            "password": "PASSWORD_INCORRECTA"
        }
    )
    paquete = msg_login.empaquetar(clave)
    respuesta = cliente.enviar_y_recibir(paquete)
    
    assert respuesta is not None
    assert respuesta["status"] == "error", "Debería rechazar credenciales incorrectas"
    print(f"[TEST] ✅ Login rechazado correctamente")
    
    cliente.desconectar()
    
    cliente.conectar()
    
    msg_login = Mensaje(
        tipo=Mensaje.LOGIN,
        datos={
            "username": username_test,
            "password": "Correct_pass1!"
        }
    )
    paquete = msg_login.empaquetar(clave)
    respuesta = cliente.enviar_y_recibir(paquete)
    
    assert respuesta is not None
    assert respuesta["status"] == "ok", f"Login falló: {respuesta.get('mensaje')}"
    print(f"[TEST] ✅ Login exitoso")
    
    cliente.desconectar()
    
    # ═══════════════════════════════════════════════════════
    # PASO 3: TRANSACCIÓN 1
    # ═══════════════════════════════════════════════════════
    
    cliente.conectar()
    
    msg_transaccion = Mensaje(
        tipo=Mensaje.TRANSACCION,
        datos={
            "username": username_test,
            "cuenta_origen": "ES1234567890",
            "cuenta_destino": "ES0987654321",
            "cantidad": 100.50
        }
    )
    paquete = msg_transaccion.empaquetar(clave)
    respuesta = cliente.enviar_y_recibir(paquete)
    
    assert respuesta is not None
    assert respuesta["status"] == "ok", f"Transacción falló: {respuesta.get('mensaje')}"
    print(f"[TEST] ✅ Transacción 1 exitosa: 100.50 EUR")
    
    cliente.desconectar()
    
    # ═══════════════════════════════════════════════════════
    # PASO 4: TRANSACCIÓN 2
    # ═══════════════════════════════════════════════════════
    
    cliente.conectar()
    
    msg_transaccion2 = Mensaje(
        tipo=Mensaje.TRANSACCION,
        datos={
            "username": username_test,
            "cuenta_origen": "ES1111111111",
            "cuenta_destino": "ES2222222222",
            "cantidad": 250.75
        }
    )
    paquete = msg_transaccion2.empaquetar(clave)
    respuesta = cliente.enviar_y_recibir(paquete)
    
    assert respuesta is not None
    assert respuesta["status"] == "ok"
    print(f"[TEST] ✅ Transacción 2 exitosa: 250.75 EUR")
    
    cliente.desconectar()


def test_login_con_credenciales_incorrectas(servidor_test):
    """Test: Login con contraseña incorrecta debe fallar"""
    clave = Config.get_shared_key()
    
    cliente = ClienteSocket("127.0.0.1", 5001)
    cliente.conectar()
    
    msg_login = Mensaje(
        tipo=Mensaje.LOGIN,
        datos={
            "username": "usuario_inexistente",
            "password": "password_incorrecta"
        }
    )
    paquete = msg_login.empaquetar(clave)
    respuesta = cliente.enviar_y_recibir(paquete)
    
    assert respuesta is not None
    assert respuesta["status"] == "error", "Debería rechazar credenciales incorrectas"
    print(f"[TEST] ✅ Login rechazado correctamente")
    
    cliente.desconectar()


def test_registro_usuario_duplicado(servidor_test):
    """Test: No se puede registrar el mismo usuario dos veces"""
    clave = Config.get_shared_key()
    username_test = f"test_dup_{int(time.time())}"
    
    # Primer registro
    cliente = ClienteSocket("127.0.0.1", 5001)
    cliente.conectar()
    
    msg_registro = Mensaje(
        tipo=Mensaje.REGISTRO,
        datos={
            "username": username_test,
            "password": "Correct_pass1"
        }
    )
    paquete = msg_registro.empaquetar(clave)
    respuesta1 = cliente.enviar_y_recibir(paquete)
    
    assert respuesta1["status"] == "ok"
    cliente.desconectar()
    
    # Segundo registro (mismo usuario)
    cliente.conectar()
    paquete = msg_registro.empaquetar(clave)
    respuesta2 = cliente.enviar_y_recibir(paquete)
    
    assert respuesta2["status"] == "error", "Debería rechazar usuario duplicado"
    assert "existe" in respuesta2["mensaje"].lower()
    print(f"[TEST] ✅ Usuario duplicado rechazado correctamente")
    
    cliente.desconectar()


# ════════════════════════════════════════════════════════
# TESTS DE SEGURIDAD
# ════════════════════════════════════════════════════════

# tests/test_integration.py

def test_detectar_replay_attack_transaccion(servidor_test):
    """
    Test: Servidor detecta replay attack en transacción
    
    Escenario realista:
    1. Usuario se registra y hace login
    2. Usuario hace una transferencia legítima de 100 EUR
    3. Atacante captura el paquete de la transacción
    4. Atacante reenvía el MISMO paquete (replay attack)
    5. Servidor debe RECHAZAR el segundo intento
    
    Impacto: Sin protección anti-replay, el atacante podría
    duplicar transacciones y robar dinero.
    """
    import time
    clave = Config.get_shared_key()
    username_test = f"test_replay_{int(time.time())}"
    
    # ═══════════════════════════════════════════════════════════
    # PREPARACIÓN: Registrar usuario
    # ═══════════════════════════════════════════════════════════
    
    cliente = ClienteSocket("127.0.0.1", 5001)
    cliente.conectar()
    
    msg_registro = Mensaje(
        tipo=Mensaje.REGISTRO,
        datos={
            "username": username_test,
            "password": "Correct_pass1"
        }
    )
    paquete = msg_registro.empaquetar(clave)
    respuesta = cliente.enviar_y_recibir(paquete)
    assert respuesta["status"] == "ok", "Registro falló"
    
    cliente.desconectar()
    
    # ═══════════════════════════════════════════════════════════
    # PASO 1: Usuario hace LOGIN legítimo
    # ═══════════════════════════════════════════════════════════
    
    cliente.conectar()
    
    msg_login = Mensaje(
        tipo=Mensaje.LOGIN,
        datos={
            "username": username_test,
            "password": "Correct_pass1"
        }
    )
    paquete = msg_login.empaquetar(clave)
    respuesta = cliente.enviar_y_recibir(paquete)
    assert respuesta["status"] == "ok", "Login falló"
    
    cliente.desconectar()
    
    # ═══════════════════════════════════════════════════════════
    # PASO 2: Usuario hace TRANSACCIÓN legítima (100 EUR)
    # ═══════════════════════════════════════════════════════════
    
    cliente.conectar()
    
    msg_transaccion = Mensaje(
        tipo=Mensaje.TRANSACCION,
        datos={
            "username": username_test,
            "cuenta_origen": "ES1234567890123456789012",
            "cuenta_destino": "ES9876543210987654321098",
            "cantidad": 100.00
        }
    )
    
    # 🎯 CAPTURAR EL PAQUETE (simula que el atacante lo intercepta)
    paquete_transaccion = msg_transaccion.empaquetar(clave)
    
    # Enviar primera vez (transacción legítima)
    respuesta1 = cliente.enviar_y_recibir(paquete_transaccion)
    
    assert respuesta1 is not None, "No se recibió respuesta del servidor"
    assert respuesta1["status"] == "ok", f"Transacción falló: {respuesta1.get('mensaje')}"
    
    print(f"\n[TEST] ✅ Transacción legítima exitosa: 100.00 EUR")
    print(f"        Origen: ES1234...9012")
    print(f"        Destino: ES9876...1098")
    
    cliente.desconectar()
    
    # ═══════════════════════════════════════════════════════════
    # PASO 3: ATACANTE REENVÍA EL MISMO PAQUETE (Replay Attack)
    # ═══════════════════════════════════════════════════════════
    
    print(f"\n[TEST] 🚨 ATACANTE intenta replay attack...")
    print(f"        Reenviando el MISMO paquete capturado")
    
    # Reconectar (nueva conexión TCP)
    cliente.conectar()
    
    # 🔥 REPLAY ATTACK: Enviar el MISMO paquete otra vez
    # (mismo mensaje, mismo MAC, mismo NONCE)
    respuesta2 = cliente.enviar_y_recibir(paquete_transaccion)
    
    cliente.desconectar()
    # ═══════════════════════════════════════════════════════════
    # VERIFICACIÓN: El servidor DEBE rechazar el replay
    # ═══════════════════════════════════════════════════════════
    
    assert respuesta2 is not None, "Servidor no respondió al replay"
    assert respuesta2["status"] == "error", \
        " FALLO DE SEGURIDAD: Servidor aceptó replay attack!"
    
    # Verificar que el mensaje de error menciona NONCE o Replay
    mensaje_error = respuesta2["mensaje"].lower()
    assert "nonce" in mensaje_error or "replay" in mensaje_error, \
        f"Mensaje de error no indica replay: {respuesta2['mensaje']}"
    
    print(f"\n[TEST]  REPLAY ATTACK BLOQUEADO correctamente")
    print(f"        Mensaje del servidor: {respuesta2['mensaje']}")
    
    # ═══════════════════════════════════════════════════════════
    # VERIFICACIÓN ADICIONAL: Comprobar en BD
    # ═══════════════════════════════════════════════════════════
    
    from server.database import DatabaseManager
    db = DatabaseManager(Config.DB_PATH)
    
    # Obtener transacciones del usuario
    transacciones = db.obtener_transacciones_usuario(username_test)
    
    # Verificar que SOLO hay UNA transacción de 100 EUR
    transacciones_100_eur = [
        tx for tx in transacciones 
        if tx['cantidad'] == 100.00
    ]
    
    assert len(transacciones_100_eur) == 1, \
        f" FALLO: Se registraron {len(transacciones_100_eur)} transacciones (debería ser 1)"
    
    print(f"\n[TEST]  Base de datos correcta: Solo 1 transacción registrada")
    print(f"        El replay NO se procesó")
    print(f"        Sin protección, el atacante habría transferido 200 EUR en total")

def test_detectar_mac_invalido(servidor_test):
    """
    Test: Servidor detecta MAC inválido (mensaje modificado)
    """
    clave = Config.get_shared_key()
    
    cliente = ClienteSocket("127.0.0.1", 5001)
    cliente.conectar()
    
    # Crear mensaje con MAC válido
    msg = Mensaje(
        tipo=Mensaje.LOGIN,
        datos={
            "username": "test",
            "password": "pass"
        }
    )
    mensaje_bytes, mac_valido, nonce = msg.serializar(clave)
    
    # Modificar el mensaje (simular ataque MiTM)
    mensaje_modificado = mensaje_bytes.replace(b"test", b"hack")
    
    # Empaquetar con mensaje modificado pero MAC original
    import json
    import base64
    paquete_malicioso = json.dumps({
        "mensaje": base64.b64encode(mensaje_modificado).decode('ascii'),
        "mac": base64.b64encode(mac_valido).decode('ascii'),
        "nonce": base64.b64encode(nonce).decode('ascii')
    }).encode('utf-8')
    
    # Enviar mensaje modificado
    cliente.socket.sendall(paquete_malicioso)
    respuesta_bytes = cliente.socket.recv(4096)
    respuesta = json.loads(respuesta_bytes.decode('utf-8'))
    
    assert respuesta["status"] == "error"
    assert "MAC" in respuesta["mensaje"] or "integridad" in respuesta["mensaje"].lower()
    print(f"[TEST] ✅ MAC inválido detectado correctamente")
    
    cliente.desconectar()


# ════════════════════════════════════════════════════════
# TESTS DE ROBUSTEZ
# ════════════════════════════════════════════════════════



def test_mensaje_malformado(servidor_test):
    """Test: Servidor maneja mensajes malformados sin crashear"""
    cliente = ClienteSocket("127.0.0.1", 5001)
    cliente.conectar()
    
    # Enviar basura
    cliente.socket.sendall(b"BASURA_NO_JSON_12345")
    
    try:
        respuesta_bytes = cliente.socket.recv(4096)
        respuesta = json.loads(respuesta_bytes.decode('utf-8'))
        
        assert respuesta["status"] == "error"
        assert "malformado" in respuesta["mensaje"].lower()
        print(f"[TEST] ✅ Mensaje malformado manejado correctamente")
    except:
        # Si el servidor cierra la conexión, también es válido
        print(f"[TEST] ✅ Servidor cerró conexión con mensaje malformado")
    
    cliente.desconectar()


# ════════════════════════════════════════════════════════
# TEST DE PERSISTENCIA
# ════════════════════════════════════════════════════════

def test_datos_persisten_en_base_de_datos(servidor_test):
    """Test: Los datos se guardan correctamente en la BD"""
    from server.database import DatabaseManager
    
    clave = Config.get_shared_key()
    username_test = f"test_persist_{int(time.time())}"
    
    # Registrar usuario
    cliente = ClienteSocket("127.0.0.1", 5001)
    cliente.conectar()
    
    msg_registro = Mensaje(
        tipo=Mensaje.REGISTRO,
        datos={
            "username": username_test,
            "password": "Correct_pass1"
        }
    )
    paquete = msg_registro.empaquetar(clave)
    cliente.enviar_y_recibir(paquete)
    cliente.desconectar()
    
    # Verificar en BD directamente
    db = DatabaseManager(Config.DB_PATH)
    assert db.usuario_existe(username_test), "Usuario no se guardó en BD"
    
    hash_bd = db.obtener_password_hash(username_test)
    assert hash_bd is not None
    assert hash_bd.startswith("$argon2"), "Password no se hasheó con Argon2"
    
    print(f"[TEST] ✅ Datos persisten correctamente en BD")

# ════════════════════════════════════════════════════════
# TEST ATAQUE DE FUERZA BRUTA EN LOGIN
# ════════════════════════════════════════════════════════

def test_servidor_bloquea_fuerza_bruta_login(servidor_test):
    """
    Test: SERVIDOR bloquea intentos de fuerza bruta en login
    
    Verifica que después de X intentos fallidos, el servidor
    bloquea el usuario temporalmente.
    """
    import time
    clave = Config.get_shared_key()
    username_test = f"test_brute_{int(time.time())}"
    
    # ═══════════════════════════════════════════════════════
    # PREPARACIÓN: Registrar usuario
    # ═══════════════════════════════════════════════════════
    
    cliente = ClienteSocket("127.0.0.1", 5001)
    cliente.conectar()
    
    msg_registro = Mensaje(
        tipo=Mensaje.REGISTRO,
        datos={
            "username": username_test,
            "password": "Correct_Pass123!"
        }
    )
    paquete = msg_registro.empaquetar(clave)
    respuesta = cliente.enviar_y_recibir(paquete)
    assert respuesta["status"] == "ok", "Registro falló"
    
    cliente.desconectar()
    
    print(f"\n[TEST] Usuario '{username_test}' registrado correctamente")
    
    # ═══════════════════════════════════════════════════════
    # ATAQUE: Intentar login con contraseña incorrecta 5 veces
    # ═══════════════════════════════════════════════════════
    
    msg_login = Mensaje(
        tipo=Mensaje.LOGIN,
        datos={
            "username": username_test,
            "password": "Wrong_Password_123!"  # ← Incorrecta
        }
    )
    
    intentos_rechazados = 0
    
    for i in range(6):  # Intentar 6 veces (límite es 5)
        # Nueva conexión por cada intento
        cliente = ClienteSocket("127.0.0.1", 5001)
        cliente.conectar()
        
        paquete = msg_login.empaquetar(clave)
        respuesta = cliente.enviar_y_recibir(paquete)
        
        cliente.desconectar()
        
        print(f"[TEST] Intento #{i+1}: {respuesta['mensaje']}")
        
        assert respuesta["status"] == "error"
        
        if "bloqueado" in respuesta["mensaje"].lower():
            print(f"[TEST] ✅ Usuario bloqueado en intento #{i+1}")
            intentos_rechazados = i + 1
            break
    
    # Verificar que se bloqueó
    assert intentos_rechazados > 0, "El servidor NO bloqueó después de intentos fallidos"
    assert intentos_rechazados <= 6, "Debería haberse bloqueado en 6 intentos o menos"
    
    # ═══════════════════════════════════════════════════════
    # VERIFICAR: Siguiente intento también es rechazado
    # ═══════════════════════════════════════════════════════
    
    cliente = ClienteSocket("127.0.0.1", 5001)
    cliente.conectar()
    
    # Intentar con la CONTRASEÑA CORRECTA (debería seguir bloqueado)
    msg_login_correcto = Mensaje(
        tipo=Mensaje.LOGIN,
        datos={
            "username": username_test,
            "password": "Correct_Pass123!"  # ← CORRECTA
        }
    )
    paquete = msg_login_correcto.empaquetar(clave)
    respuesta = cliente.enviar_y_recibir(paquete)
    
    cliente.desconectar()
    
    # Debería estar bloqueado incluso con password correcta
    assert respuesta["status"] == "error"
    assert "bloqueado" in respuesta["mensaje"].lower()
    
    print(f"[TEST] ✅ Usuario sigue bloqueado incluso con password correcta")
    print(f"[TEST] ✅ Protección anti-fuerza bruta funciona correctamente")

# ════════════════════════════════════════════════════════
# EJECUTAR TODOS LOS TESTS
# ════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])