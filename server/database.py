import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

def _adapt_datetime(dt: datetime) -> str:
    """Convierte datetime a string ISO para SQLite"""
    return dt.isoformat()

def _convert_datetime(val: bytes) -> datetime:
    """Convierte string ISO de SQLite a datetime"""
    return datetime.fromisoformat(val.decode())

# Registrar los adaptadores (solo una vez)
sqlite3.register_adapter(datetime, _adapt_datetime)
sqlite3.register_converter("TIMESTAMP", _convert_datetime)

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
                conn.executescript(sql_path.read_text(encoding='utf-8'))
            else:
                print("⚠️  Advertencia: No se encontró init_db.sql")
    
    @contextmanager
    def get_connection(self):
        # AÑADIR: detect_types para usar los convertidores (solucion para prolema  con datetime deprecated)
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
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