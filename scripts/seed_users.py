#!/usr/bin/env python3
"""
scripts/seed_users.py
─────────────────────────────────────────────────────────────────────────────
Pobla la base de datos con usuarios de prueba pre-registrados.
Usa Argon2id con los MISMOS parámetros definidos en common/constantes.py.

Uso:
    python scripts/seed_users.py                  # BD por defecto (database/usuarios.db)
    python scripts/seed_users.py --db ruta/bd.db  # BD personalizada
    python scripts/seed_users.py --reset          # Borra usuarios existentes antes de insertar
─────────────────────────────────────────────────────────────────────────────
"""

import sqlite3
import sys
import argparse
from pathlib import Path
from datetime import datetime

# ── Dependencia externa ────────────────────────────────────────────────────────
try:
    from argon2 import PasswordHasher
except ImportError:
    print("[ERROR] Dependencia no encontrada. Instala argon2-cffi:")
    print("        pip install argon2-cffi")
    sys.exit(1)

# ── Parámetros Argon2id (espejo de common/constantes.py) ──────────────────────
ARGON2_TIME_COST    = 3       # iteraciones
ARGON2_MEMORY_COST  = 65536  # 64 MB
ARGON2_PARALLELISM  = 4       # hilos
ARGON2_HASH_LEN     = 32      # bytes
ARGON2_SALT_LEN     = 16      # bytes

# ── Ruta por defecto de la BD ──────────────────────────────────────────────────
DEFAULT_DB_PATH = Path(__file__).parent.parent / "database" / "usuarios.db"

# ══════════════════════════════════════════════════════════════════════════════
# USUARIOS DE PRUEBA
# Modifica esta lista para añadir, quitar o cambiar usuarios seed.
# Campos: username, password (en claro — se hashea aquí mismo)
# ══════════════════════════════════════════════════════════════════════════════
USUARIOS_SEED = [
    {"username": "ralsei",   "password": "ChocoMint#04"},
    {"username": "susie",     "password": "Godzilla#003"},
    {"username": "kris",   "password": "DiloMansana#04"},
    {"username": "admin",   "password": "Admin#Secure99"},
    {"username": "test",    "password": "Test#0000"},
]


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIONES
# ══════════════════════════════════════════════════════════════════════════════

def crear_hasher() -> PasswordHasher:
    """Devuelve un PasswordHasher configurado igual que el sistema real."""
    return PasswordHasher(
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_HASH_LEN,
        salt_len=ARGON2_SALT_LEN,
    )


def conectar_bd(db_path: Path) -> sqlite3.Connection:
    """Abre la conexión a la BD. Falla si el archivo no existe."""
    if not db_path.exists():
        print(f"[ERROR] No se encontró la base de datos en: {db_path}")
        print("        Ejecuta primero:  python scripts/inicializar_bd.py")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def tabla_existe(conn: sqlite3.Connection, nombre: str) -> bool:
    """Comprueba que la tabla existe en la BD."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (nombre,)
    )
    return cur.fetchone() is not None


def reset_usuarios(conn: sqlite3.Connection) -> None:
    """Elimina todos los usuarios existentes (y sus transacciones por FK)."""
    conn.execute("DELETE FROM transacciones")
    conn.execute("DELETE FROM usuarios")
    conn.commit()
    print("[*] Tabla usuarios vaciada (--reset)\n")


def insertar_usuarios(conn: sqlite3.Connection, usuarios: list, ph: PasswordHasher) -> None:
    """Inserta los usuarios hasheando cada contraseña con Argon2id."""
    print(f"[*] Insertando {len(usuarios)} usuarios...\n")
    print(f"    {'Usuario':<15} {'Estado'}")
    print(f"    {'-'*15} {'-'*30}")

    insertados = 0
    omitidos   = 0

    for u in usuarios:
        username = u["username"]
        password = u["password"]

        try:
            # Verificar si ya existe
            cur = conn.execute(
                "SELECT id FROM usuarios WHERE username = ?", (username,)
            )
            if cur.fetchone():
                print(f"    {username:<15} OMITIDO (ya existe)")
                omitidos += 1
                continue

            # Hashear con Argon2id
            password_hash = ph.hash(password)

            conn.execute(
                "INSERT INTO usuarios (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, password_hash, datetime.now().isoformat())
            )
            conn.commit()
            print(f"    {username:<15} OK")
            insertados += 1

        except Exception as e:
            conn.rollback()
            print(f"    {username:<15} ERROR -> {e}")

    print()
    print(f"[OK] Resumen: {insertados} insertados, {omitidos} omitidos.")


def mostrar_usuarios(conn: sqlite3.Connection) -> None:
    """Muestra el estado final de la tabla usuarios."""
    cur = conn.execute(
        "SELECT id, username, created_at FROM usuarios ORDER BY id"
    )
    filas = cur.fetchall()

    print()
    print("─" * 60)
    print("   ESTADO FINAL — tabla usuarios")
    print("─" * 60)
    print(f"   {'ID':<5} {'Username':<15} {'Creado en'}")
    print(f"   {'─'*4} {'─'*14} {'─'*25}")
    for f in filas:
        print(f"   {f['id']:<5} {f['username']:<15} {f['created_at']}")
    print(f"   Total: {len(filas)} usuarios")
    print("─" * 60)


# ══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Pobla la BD con usuarios de prueba (sin transacciones)."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Ruta al archivo .db (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Elimina todos los usuarios existentes antes de insertar",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("   SEED DE USUARIOS — PAI1-STX".center(60))
    print("=" * 60)
    print(f"\n[*] Base de datos : {args.db}")
    print(f"[*] Hasher        : Argon2id")
    print(f"[*] Parámetros    : time={ARGON2_TIME_COST}, mem={ARGON2_MEMORY_COST}KB, "
          f"par={ARGON2_PARALLELISM}, hash={ARGON2_HASH_LEN}B\n")

    conn = conectar_bd(args.db)

    # Verificar que las tablas existen
    for tabla in ("usuarios", "transacciones", "nonces"):
        if not tabla_existe(conn, tabla):
            print(f"[ERROR] La tabla '{tabla}' no existe.")
            print("        Ejecuta primero el script de inicialización de la BD.")
            conn.close()
            sys.exit(1)

    if args.reset:
        reset_usuarios(conn)

    ph = crear_hasher()
    insertar_usuarios(conn, USUARIOS_SEED, ph)
    mostrar_usuarios(conn)

    conn.close()
    print("\n[OK] Proceso completado.\n")


if __name__ == "__main__":
    main()