import pytest
from common.crypto__utils import generar_nonce, calcular_mac, verificar_mac
from common.constantes import NONCE_SIZE, MAC_SIZE

def test_generar_nonce():
    """Test: Los NONCEs deben ser únicos"""
    nonce1 = generar_nonce()
    nonce2 = generar_nonce()
    
    assert len(nonce1) == NONCE_SIZE
    assert len(nonce2) == NONCE_SIZE
    assert nonce1 != nonce2  # Deben ser diferentes

def test_calcular_mac():
    """Test: MAC debe tener tamaño correcto"""
    clave = b"clave_de_prueba_32_bytes_long!@#"
    mensaje = b"Hola mundo"
    nonce = generar_nonce()
    
    mac = calcular_mac(clave, mensaje, nonce)
    
    assert len(mac) == MAC_SIZE
    assert isinstance(mac, bytes)

def test_verificar_mac_valido():
    """Test: Verificar MAC correcto debe retornar True"""
    clave = b"clave_de_prueba_32_bytes_long!@#"
    mensaje = b"Transferencia: 100 EUR"
    nonce = generar_nonce()
    
    mac = calcular_mac(clave, mensaje, nonce)
    resultado = verificar_mac(clave, mensaje, nonce, mac)
    
    assert resultado is True

def test_verificar_mac_invalido():
    """Test: MAC modificado debe ser detectado"""
    clave = b"clave_de_prueba_32_bytes_long!@#"
    mensaje = b"Transferencia: 100 EUR"
    nonce = generar_nonce()
    
    mac_original = calcular_mac(clave, mensaje, nonce)
    
    # Simular ataque: modificar el mensaje
    mensaje_modificado = b"Transferencia: 999 EUR"
    resultado = verificar_mac(clave, mensaje_modificado, nonce, mac_original)
    
    assert resultado is False  # Debe detectar la modificación

def test_mac_diferente_con_diferente_nonce():
    """Test: Mismo mensaje con diferente NONCE produce MAC diferente"""
    clave = b"clave_de_prueba_32_bytes_long!@#"
    mensaje = b"Mismo mensaje"
    
    nonce1 = generar_nonce()
    nonce2 = generar_nonce()
    
    mac1 = calcular_mac(clave, mensaje, nonce1)
    mac2 = calcular_mac(clave, mensaje, nonce2)
    
    assert mac1 != mac2  # MACs deben ser diferentes