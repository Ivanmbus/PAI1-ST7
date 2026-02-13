# 🚀 Guía de Desarrollo del Proyecto PAI1-INTEGRIDOS

## Metodología de Desarrollo Recomendada

Esta guía te llevará desde cero hasta un proyecto funcional siguiendo un enfoque **incremental y testeable**.

---

## 📅 Fase 0: Preparación (Día 1 - 30 minutos)

### 1. Configurar el entorno de desarrollo

```bash
# Crear estructura básica
mkdir PAI1-STX
cd PAI1-STX

# Crear directorios principales
mkdir -p cliente servidor common tests database logs docs config scripts

# Crear archivos vacíos iniciales
touch cliente/__init__.py servidor/__init__.py common/__init__.py tests/__init__.py
touch run_servidor.py run_cliente.py
touch requirements.txt .gitignore README.md

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Crear `requirements.txt`

```txt
cryptography>=42.0.0
argon2-cffi>=23.1.0
python-dotenv>=1.0.0
colorama>=0.4.6
pytest>=7.4.0
```

```bash
pip install -r requirements.txt
```

### 3. Crear `.gitignore`

```gitignore
# Archivos sensibles
.env
*.key
config/shared_key.key

# Base de datos
*.db
*.sqlite
*.sqlite3

# Logs
logs/*.log

# Python
__pycache__/
*.pyc
*.pyo
venv/
env/

# IDE
.vscode/
.idea/
```

---

## 🏗️ Fase 1: Fundamentos Criptográficos (Día 1-2)

**Objetivo:** Implementar las funciones de seguridad básicas antes de hacer comunicación.

### Paso 1.1: Crear `common/constantes.py`

```python
# common/constantes.py
"""
Constantes criptográficas del sistema
"""

# Tamaños
MAC_SIZE = 32  # bytes (HMAC-SHA256 produce 32 bytes)
NONCE_SIZE = 32  # bytes (256 bits)
KEY_SIZE = 32  # bytes (256 bits para HMAC)

# Algoritmos
HASH_ALGORITHM = "sha256"
MAC_ALGORITHM = "HMAC-SHA256"
PASSWORD_HASHER = "Argon2id"

# Argon2 parámetros
ARGON2_TIME_COST = 3  # iteraciones
ARGON2_MEMORY_COST = 65536  # 64 MB
ARGON2_PARALLELISM = 4  # hilos
ARGON2_HASH_LEN = 32  # bytes
ARGON2_SALT_LEN = 16  # bytes

# Configuración de red
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000
BUFFER_SIZE = 4096

# Mensajes
ENCODING = "utf-8"
```

### Paso 1.2: Crear `common/config.py`

```python
# common/config.py
"""
Gestión de configuración
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import base64

load_dotenv()

class Config:
    # Red
    SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 5000))
    
    # Base de datos
    DB_PATH = os.getenv("DB_PATH", "./database/usuarios.db")
    
    # Logs
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/servidor.log")
    
    # Clave compartida (en base64)
    SHARED_KEY_B64 = os.getenv("SHARED_KEY")
    
    @classmethod
    def get_shared_key(cls) -> bytes:
        """Obtiene la clave compartida decodificada"""
        if cls.SHARED_KEY_B64:
            return base64.b64decode(cls.SHARED_KEY_B64)
        # Si no existe, cargar desde archivo
        key_path = Path("config/shared_key.key")
        if key_path.exists():
            return key_path.read_bytes()
        raise ValueError("No se encontró la clave compartida")
```

### Paso 1.3: Crear script para generar clave compartida

```python
# scripts/generar_clave.py
"""
Genera una clave compartida criptográficamente segura
"""
import secrets
import base64
from pathlib import Path

def generar_clave_compartida():
    """Genera una clave de 256 bits (32 bytes)"""
    clave = secrets.token_bytes(32)
    
    # Guardar en archivo binario
    key_path = Path("config/shared_key.key")
    key_path.parent.mkdir(exist_ok=True)
    key_path.write_bytes(clave)
    
    # También mostrar en base64 para .env
    clave_b64 = base64.b64encode(clave).decode()
    
    print("✅ Clave compartida generada exitosamente")
    print(f"📁 Guardada en: {key_path}")
    print(f"\n🔑 Para usar en .env, añade esta línea:")
    print(f"SHARED_KEY={clave_b64}")
    
    return clave

if __name__ == "__main__":
    generar_clave_compartida()
```

```bash
python scripts/generar_clave.py
```

### Paso 1.4: Crear `.env`

```bash
# .env
SERVER_HOST=127.0.0.1
SERVER_PORT=5000
DB_PATH=./database/usuarios.db
LOG_LEVEL=INFO
LOG_FILE=./logs/servidor.log
SHARED_KEY=tu_clave_en_base64_generada_arriba
```

### Paso 1.5: Implementar funciones criptográficas básicas

```python
# common/crypto_utils.py
"""
Utilidades criptográficas compartidas
"""
import hmac
import hashlib
import secrets
from typing import Tuple
from .constantes import MAC_SIZE, NONCE_SIZE

def generar_nonce() -> bytes:
    """
    Genera un NONCE criptográficamente seguro
    
    Returns:
        bytes: NONCE de 32 bytes
    """
    return secrets.token_bytes(NONCE_SIZE)

def calcular_mac(clave: bytes, mensaje: bytes, nonce: bytes) -> bytes:
    """
    Calcula el MAC de un mensaje usando HMAC-SHA256
    
    Args:
        clave: Clave compartida
        mensaje: Datos a proteger
        nonce: NONCE único para este mensaje
    
    Returns:
        bytes: MAC de 32 bytes
    """
    datos = mensaje + nonce
    return hmac.new(clave, datos, hashlib.sha256).digest()

def verificar_mac(clave: bytes, mensaje: bytes, nonce: bytes, mac_recibido: bytes) -> bool:
    """
    Verifica el MAC de un mensaje usando comparación en tiempo constante
    
    Args:
        clave: Clave compartida
        mensaje: Datos recibidos
        nonce: NONCE recibido
        mac_recibido: MAC recibido del cliente
    
    Returns:
        bool: True si el MAC es válido
    """
    mac_calculado = calcular_mac(clave, mensaje, nonce)
    return hmac.compare_digest(mac_calculado, mac_recibido)
```

### ✅ TEST Fase 1: Crear `tests/test_crypto.py`

```python
# tests/test_crypto.py
import pytest
from common.crypto_utils import generar_nonce, calcular_mac, verificar_mac
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
```

```bash
# Ejecutar tests
pytest tests/test_crypto.py -v
```

---

## 💾 Fase 2: Base de Datos (Día 2-3)

### Paso 2.1: Crear esquema SQL

```sql
-- database/init_db.sql

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de transacciones
CREATE TABLE IF NOT EXISTS transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    cuenta_origen TEXT NOT NULL,
    cuenta_destino TEXT NOT NULL,
    cantidad REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mac_verificado BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (username) REFERENCES usuarios(username)
);

-- Tabla de NONCEs (anti-replay)
CREATE TABLE IF NOT EXISTS nonces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valor BLOB UNIQUE NOT NULL,
    expira TIMESTAMP NOT NULL,
    usado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar búsquedas
CREATE UNIQUE INDEX IF NOT EXISTS idx_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_nonce_valor ON nonces(valor);
CREATE INDEX IF NOT EXISTS idx_nonce_expira ON nonces(expira);
```

### Paso 2.2: Implementar gestor de base de datos

```python
# servidor/database.py
"""
Gestión de base de datos
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._inicializar_bd()
    
    def _inicializar_bd(self):
        """Crea las tablas si no existen"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with self.get_connection() as conn:
            # Leer y ejecutar script SQL
            sql_path = Path("database/init_db.sql")
            if sql_path.exists():
                conn.executescript(sql_path.read_text())
            else:
                print("⚠️  Advertencia: No se encontró init_db.sql")
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    # === GESTIÓN DE USUARIOS ===
    
    def crear_usuario(self, username: str, password_hash: str) -> bool:
        """
        Crea un nuevo usuario
        
        Returns:
            bool: True si se creó exitosamente, False si ya existe
        """
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
            return True
        except sqlite3.IntegrityError:
            return False  # Usuario ya existe
    
    def obtener_password_hash(self, username: str) -> Optional[str]:
        """Obtiene el hash de contraseña de un usuario"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT password_hash FROM usuarios WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            return row['password_hash'] if row else None
    
    def usuario_existe(self, username: str) -> bool:
        """Verifica si un usuario existe"""
        return self.obtener_password_hash(username) is not None
    
    # === GESTIÓN DE NONCES (ANTI-REPLAY) ===
    
    def validar_nonce(self, nonce: bytes, duracion_minutos: int = 5) -> bool:
        """
        Valida que un NONCE no haya sido usado y lo registra
        
        Args:
            nonce: NONCE a validar
            duracion_minutos: Tiempo de validez del NONCE
        
        Returns:
            bool: True si el NONCE es válido (no usado), False si ya fue usado
        """
        with self.get_connection() as conn:
            # Verificar si el NONCE ya existe
            cursor = conn.execute(
                "SELECT id FROM nonces WHERE valor = ?",
                (nonce,)
            )
            if cursor.fetchone():
                return False  # NONCE ya usado - Ataque replay detectado!
            
            # Registrar el NONCE con fecha de expiración
            expira = datetime.now() + timedelta(minutes=duracion_minutos)
            conn.execute(
                "INSERT INTO nonces (valor, expira) VALUES (?, ?)",
                (nonce, expira)
            )
            return True
    
    def limpiar_nonces_expirados(self):
        """Elimina NONCEs que ya expiraron"""
        with self.get_connection() as conn:
            ahora = datetime.now()
            cursor = conn.execute(
                "DELETE FROM nonces WHERE expira < ?",
                (ahora,)
            )
            eliminados = cursor.rowcount
            return eliminados
    
    # === GESTIÓN DE TRANSACCIONES ===
    
    def registrar_transaccion(
        self,
        username: str,
        cuenta_origen: str,
        cuenta_destino: str,
        cantidad: float,
        mac_verificado: bool = True
    ) -> int:
        """
        Registra una transacción
        
        Returns:
            int: ID de la transacción creada
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO transacciones 
                   (username, cuenta_origen, cuenta_destino, cantidad, mac_verificado)
                   VALUES (?, ?, ?, ?, ?)""",
                (username, cuenta_origen, cuenta_destino, cantidad, mac_verificado)
            )
            return cursor.lastrowid
    
    def obtener_transacciones_usuario(self, username: str) -> List[dict]:
        """Obtiene todas las transacciones de un usuario"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """SELECT * FROM transacciones 
                   WHERE username = ? 
                   ORDER BY timestamp DESC""",
                (username,)
            )
            return [dict(row) for row in cursor.fetchall()]
```

### Paso 2.3: Implementar hashing de contraseñas

```python
# servidor/crypto_server.py
"""
Funciones criptográficas del servidor
"""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import hmac
from common.constantes import (
    ARGON2_TIME_COST,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_HASH_LEN,
    ARGON2_SALT_LEN
)

# Configurar Argon2
ph = PasswordHasher(
    time_cost=ARGON2_TIME_COST,
    memory_cost=ARGON2_MEMORY_COST,
    parallelism=ARGON2_PARALLELISM,
    hash_len=ARGON2_HASH_LEN,
    salt_len=ARGON2_SALT_LEN
)

def hashear_password(password: str) -> str:
    """
    Genera hash Argon2id de una contraseña
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        str: Hash de la contraseña
    """
    return ph.hash(password)

def verificar_password(password_hash: str, password: str) -> bool:
    """
    Verifica una contraseña contra su hash usando comparación segura
    
    Args:
        password_hash: Hash almacenado
        password: Contraseña a verificar
    
    Returns:
        bool: True si la contraseña es correcta
    """
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False

def secure_compare(a: bytes, b: bytes) -> bool:
    """
    Comparación en tiempo constante (protección contra timing attacks)
    
    Args:
        a: Primer valor
        b: Segundo valor
    
    Returns:
        bool: True si son iguales
    """
    return hmac.compare_digest(a, b)
```

### ✅ TEST Fase 2: Crear `tests/test_database.py`

```python
# tests/test_database.py
import pytest
from pathlib import Path
from servidor.database import DatabaseManager
from servidor.crypto_server import hashear_password

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
```

```bash
pytest tests/test_database.py -v
```

---

## 📡 Fase 3: Protocolo de Comunicación (Día 3-4)

### Paso 3.1: Definir protocolo de mensajes

```python
# common/protocolo.py
"""
Protocolo de comunicación cliente-servidor
"""
import json
import base64
from typing import Dict, Any, Tuple
from .crypto_utils import calcular_mac, generar_nonce
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
```

---

## 🎯 Próximos Pasos (Continúa en siguiente respuesta...)

La guía continúa con:
- **Fase 4:** Implementar Cliente (socket, interfaz CLI)
- **Fase 5:** Implementar Servidor (listener, manejo de sesiones)
- **Fase 6:** Integración y Testing E2E
- **Fase 7:** Logging y Evidencias
- **Fase 8:** Documentación y Empaquetado

---

## 📊 Resumen del Progreso Hasta Ahora

```
✅ Fase 0: Preparación (estructura, dependencias)
✅ Fase 1: Criptografía básica (MAC, NONCE, tests)
✅ Fase 2: Base de datos (schema, gestor, Argon2, tests)
✅ Fase 3: Protocolo de mensajes (serialización, empaquetado)
⬜ Fase 4: Cliente
⬜ Fase 5: Servidor
⬜ Fase 6: Integración
⬜ Fase 7: Logs
⬜ Fase 8: Documentación
```

---

## ⏱️ Estimación de Tiempos

| Fase | Tiempo Estimado | Dificultad |
|------|----------------|------------|
| Fase 0-1 | 2-3 horas | ⭐⭐ |
| Fase 2 | 3-4 horas | ⭐⭐⭐ |
| Fase 3 | 2 horas | ⭐⭐ |
| Fase 4 | 4-5 horas | ⭐⭐⭐ |
| Fase 5 | 5-6 horas | ⭐⭐⭐⭐ |
| Fase 6 | 3-4 horas | ⭐⭐⭐ |
| Fase 7 | 2 horas | ⭐⭐ |
| Fase 8 | 3-4 horas | ⭐⭐ |
| **TOTAL** | **24-32 horas** | |

**Recomendación:** Distribuir en 4-5 días de trabajo efectivo.

---

¿Quieres que continúe con las Fases 4-8? 🚀