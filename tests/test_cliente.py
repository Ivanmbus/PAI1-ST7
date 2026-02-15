import pytest
from unittest.mock import Mock, patch
from client.communicacion import ClienteSocket
from client.crypto_client import preparar_mensaje_seguro
from common.crypto__utils import generar_nonce, verificar_mac

def test_preparar_mensaje_seguro():
    """Test: Preparar mensaje con MAC y NONCE"""
    clave = b"clave_de_prueba_32_bytes_long!@#"
    mensaje = b'{"tipo":"login","datos":{}}'
    
    msg, mac, nonce = preparar_mensaje_seguro(clave, mensaje)
    
    # Verificar que se generaron correctamente
    assert msg == mensaje
    assert len(mac) == 32  # HMAC-SHA256
    assert len(nonce) == 32
    
    # Verificar que el MAC es válido
    assert verificar_mac(clave, mensaje, nonce, mac)

def test_cliente_socket_conectar():
    """Test: Conexión del socket"""
    # Mock del socket
    with patch('socket.socket') as mock_socket:
        cliente = ClienteSocket("127.0.0.1", 5000)
        resultado = cliente.conectar()
        
        assert resultado is True
        mock_socket.assert_called_once()

def test_cliente_socket_enviar():
    """Test: Envío de datos"""
    with patch('socket.socket') as mock_socket:
        cliente = ClienteSocket()
        cliente.socket = Mock()
        
        datos = b"test data"
        resultado = cliente.enviar(datos)
        
        assert resultado is True
        cliente.socket.sendall.assert_called_once_with(datos)