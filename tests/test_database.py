# tests/test_database.py
import pytest
from pathlib import Path
from server.database import DatabaseManager
from server.crypto_server import hashear_password

@pytest.fixture
def db():
    """Fixture: Base de datos temporal para tests"""
    db_path = "test_db.sqlite"
    db_manager = DatabaseManager(db_path)
    yield db_manager
    # Cleanup
    Path(db_path).unlink(missing_ok=True)

def test_crear_usuario(db):
    """Test: Crear usuario nuevo debe funcionar"""
    password_hash = hashear_password("MiContraseña123!")
    resultado = db.crear_usuario("juan", password_hash)
    
    assert resultado is True
    assert db.usuario_existe("juan")

def test_crear_usuario_duplicado(db):
    """Test: No se puede crear usuario duplicado"""
    password_hash = hashear_password("MiContraseña123!")
    db.crear_usuario("juan", password_hash)
    
    resultado = db.crear_usuario("juan", password_hash)
    
    assert resultado is False

def test_validar_nonce_unico(db):
    """Test: NONCE único debe ser aceptado"""
    nonce = b"nonce_unico_12345678901234567890"
    
    resultado = db.validar_nonce(nonce)
    
    assert resultado is True

def test_detectar_replay_attack(db):
    """Test: NONCE duplicado debe ser rechazado"""
    nonce = b"nonce_usado_12345678901234567890"
    
    # Primera vez: OK
    resultado1 = db.validar_nonce(nonce)
    assert resultado1 is True
    
    # Segunda vez: RECHAZO (replay attack)
    resultado2 = db.validar_nonce(nonce)
    assert resultado2 is False

def test_registrar_transaccion(db):
    """Test: Registrar transacción debe funcionar"""
    # Primero crear usuario
    password_hash = hashear_password("pass123")
    db.crear_usuario("juan", password_hash)
    
    # Registrar transacción
    tx_id = db.registrar_transaccion(
        username="juan",
        cuenta_origen="ES1234",
        cuenta_destino="ES5678",
        cantidad=100.50,
        mac_verificado=True
    )
    
    assert tx_id > 0
    
    # Verificar que se guardó
    transacciones = db.obtener_transacciones_usuario("juan")
    assert len(transacciones) == 1
    assert transacciones[0]['cantidad'] == 100.50