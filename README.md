# 🔒 PAI1-INTEGRIDOS

## Sistema de Verificación de Integridad para Entidad Financiera

---

## 📋 Tabla de Contenidos

- [Estructura del Proyecto](#estructura-del-proyecto)
- [Descripción de Carpetas](#descripción-de-carpetas-principales)
- [Archivos Clave](#archivos-clave)
- [Instalación y Configuración](#instalación-y-configuración)
- [Uso del Sistema](#uso-del-sistema)
- [Testing](#testing)
- [Entregable Final](#entregable-final)

---

## 🏗️ Estructura del Proyecto

```
PAI1-STX/
│
├── 📁 cliente/                          # Módulo del Cliente
│   ├── 📄 __init__.py                   # Inicializador del paquete
│   ├── 📄 cliente_gui.py                # Interfaz gráfica (Tkinter/PyQt - OPCIONAL)
│   ├── 📄 cliente_cli.py                # Interfaz línea de comandos (PRINCIPAL)
│   ├── 📄 comunicacion.py               # Gestión de sockets del cliente
│   └── 📄 crypto_client.py              # Funciones criptográficas (MAC, NONCE)
│
├── 📁 servidor/                         # Módulo del Servidor
│   ├── 📄 __init__.py                   # Inicializador del paquete
│   ├── 📄 servidor.py                   # Socket listener principal (multihilo)
│   ├── 📄 autenticacion.py              # Lógica de login/registro/sesiones
│   ├── 📄 transacciones.py              # Gestión de transferencias bancarias
│   ├── 📄 crypto_server.py              # Funciones criptográficas (verificación MAC)
│   └── 📄 database.py                   # Gestión de base de datos (SQLite/PostgreSQL)
│
├── 📁 common/                           # Módulo Compartido (cliente y servidor)
│   ├── 📄 __init__.py                   # Inicializador del paquete
│   ├── 📄 protocolo.py                  # Definición del protocolo de mensajes JSON
│   ├── 📄 config.py                     # Configuración compartida (host, puerto)
│   └── 📄 constantes.py                 # Constantes (tamaños clave, algoritmos)
│
├── 📁 tests/                            # Suite de Tests
│   ├── 📄 __init__.py                   # Inicializador del paquete de tests
│   ├── 📄 test_mac.py                   # Tests de verificación de integridad (MAC)
│   ├── 📄 test_nonce.py                 # Tests anti-replay (NONCE)
│   ├── 📄 test_argon2.py                # Tests de hashing de contraseñas
│   ├── 📄 test_timing.py                # Tests de protección contra timing attacks
│   └── 📄 test_integration.py           # Tests de integración end-to-end
│
├── 📁 database/                         # Archivos de Base de Datos
│   ├── 📄 init_db.sql                   # Script SQL de inicialización (tablas)
│   ├── 📄 seed_users.sql                # Script para usuarios pre-registrados
│   └── 📄 usuarios.db                   # Base de datos SQLite (se genera automáticamente)
│
├── 📁 logs/                             # Archivos de Logs (evidencias)
│   ├── 📄 servidor.log                  # Log de eventos del servidor
│   ├── 📄 transacciones.log             # Log de todas las transacciones
│   ├── 📄 seguridad.log                 # Log de intentos de ataque detectados
│   └── 📄 cliente.log                   # Log de actividad del cliente (opcional)
│
├── 📁 docs/                             # Documentación del Proyecto
│   ├── 📄 Manual_PAI1.pdf               # Manual de despliegue y uso (ENTREGABLE)
│   ├── 📄 arquitectura.png              # Diagrama de arquitectura
│   └── 📄 decisiones_tecnicas.md        # Documento de decisiones técnicas
│
├── 📁 config/                           # Archivos de Configuración
│   ├── 📄 .env.example                  # Ejemplo de variables de entorno
│   ├── 📄 server_config.json            # Configuración del servidor
│   └── 📄 shared_key.key                # Clave compartida (NO SUBIR A GIT)
│
├── 📁 scripts/                          # Scripts de Utilidad
│   ├── 📄 generar_clave.py              # Script para generar clave compartida
│   ├── 📄 limpiar_nonces.py             # Script para limpiar NONCEs expirados
│   └── 📄 inicializar_bd.py             # Script para inicializar base de datos
│
├── 📄 requirements.txt                  # Dependencias Python del proyecto
├── 📄 .env                              # Variables de entorno (NO SUBIR A GIT)
├── 📄 .gitignore                        # Archivos a ignorar en Git
├── 📄 README.md                         # Documentación general del proyecto
├── 📄 run_servidor.py                   # Script principal para iniciar servidor
├── 📄 run_cliente.py                    # Script principal para iniciar cliente
└── 📄 LICENCIA.txt                      # Licencia del proyecto (opcional)
```

---

## 📚 Descripción de Carpetas Principales

### 📁 `cliente/`
Contiene toda la lógica del lado del cliente:
- Interfaz de usuario (CLI o GUI)
- Generación de NONCEs y cálculo de MACs
- Envío de mensajes al servidor

### 📁 `servidor/`
Contiene toda la lógica del lado del servidor:
- Listener de sockets (acepta múltiples clientes)
- Verificación de integridad (MAC y NONCE)
- Autenticación con Argon2id
- Gestión de transacciones

### 📁 `common/`
Código compartido entre cliente y servidor:
- Protocolo de comunicación (formato de mensajes)
- Constantes (tamaños de clave, algoritmos)
- Utilidades comunes

### 📁 `tests/`
Suite completa de tests unitarios e integración:
- Tests de funciones criptográficas
- Tests de protección contra ataques
- Tests end-to-end del flujo completo

### 📁 `database/`
Todo relacionado con almacenamiento:
- Scripts SQL de inicialización
- Base de datos SQLite
- Scripts de seed para usuarios de prueba

### 📁 `logs/`
Archivos de registro para evidencias:
- Logs de servidor (conexiones, errores)
- Logs de transacciones (auditoría)
- Logs de seguridad (ataques detectados)

### 📁 `docs/`
Documentación del proyecto:
- Manual técnico (entregable)
- Diagramas de arquitectura
- Decisiones de diseño

### 📁 `config/`
Archivos de configuración sensibles:
- Variables de entorno
- Clave compartida para MAC
- Configuraciones de servidor

### 📁 `scripts/`
Scripts de utilidad y administración:
- Generación de claves
- Mantenimiento de base de datos
- Limpieza de NONCEs expirados

---

## 🔑 Archivos Clave

### `requirements.txt`

```txt
cryptography>=42.0.0        # Para HMAC-SHA256 y derivación de claves
argon2-cffi>=23.1.0        # Para hashing de contraseñas con Argon2id
python-dotenv>=1.0.0       # Para gestión de variables de entorno
colorama>=0.4.6            # Para CLI con colores (opcional)
```

### `.env` (ejemplo)

```bash
# Configuración del servidor
SERVER_HOST=127.0.0.1
SERVER_PORT=5000

# Clave compartida para MAC (en producción, usar archivo .key)
SHARED_KEY=tu_clave_secreta_de_256_bits_en_base64

# Configuración de base de datos
DB_PATH=./database/usuarios.db

# Configuración de logs
LOG_LEVEL=INFO
LOG_FILE=./logs/servidor.log
```

### `.gitignore`

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
*.pyd
.Python
venv/
env/

# IDE
.vscode/
.idea/
*.swp
```

---

## 🚀 Instalación y Configuración

### 1️⃣ Configurar entorno

```bash
# Crear directorio del proyecto
mkdir PAI1-STX
cd PAI1-STX

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Generar clave compartida

```bash
python scripts/generar_clave.py
```

Este script generará una clave secreta de 256 bits que será compartida entre cliente y servidor.

### 3️⃣ Inicializar base de datos

```bash
python scripts/inicializar_bd.py
```

Este script creará:
- Tabla de usuarios
- Tabla de transacciones
- Tabla de NONCEs
- Usuarios pre-registrados para pruebas

---

## 💻 Uso del Sistema

### Iniciar el Servidor

```bash
# Terminal 1
python run_servidor.py
```

**Salida esperada:**
```
[INFO] Cargando configuración...
[INFO] Clave compartida cargada correctamente
[INFO] Base de datos inicializada
[INFO] Servidor iniciado en 127.0.0.1:5000
[INFO] Esperando conexiones de clientes...
```

### Iniciar el Cliente

```bash
# Terminal 2
python run_cliente.py
```

**Menú principal:**
```
╔════════════════════════════════════════╗
║   SISTEMA BANCARIO - CLIENTE          ║
╚════════════════════════════════════════╝

[1] Registro
[2] Login
[3] Salir

Seleccione una opción:
```

### Flujo de Registro

```
Opción: 1

╔════════════════════════════════════════╗
║            REGISTRO                    ║
╚════════════════════════════════════════╝

Nombre de usuario: juan
Contraseña: MiContraseña123!

[✓] Generando NONCE...
[✓] Calculando MAC...
[✓] Enviando solicitud al servidor...
[✓] Usuario registrado exitosamente
```

### Flujo de Login

```
Opción: 2

╔════════════════════════════════════════╗
║              LOGIN                     ║
╚════════════════════════════════════════╝

Nombre de usuario: juan
Contraseña: MiContraseña123!

[✓] Autenticación exitosa
[✓] Sesión iniciada

────────────────────────────────────────
    MENÚ DE USUARIO
────────────────────────────────────────
[1] Realizar transacción
[2] Cerrar sesión

Seleccione una opción:
```

### Realizar Transacción

```
Opción: 1

╔════════════════════════════════════════╗
║         NUEVA TRANSACCIÓN              ║
╚════════════════════════════════════════╝

Cuenta origen: ES1234567890
Cuenta destino: ES0987654321
Cantidad: 500.00

[✓] Generando NONCE único...
[✓] Calculando MAC de transacción...
[✓] Enviando al servidor...
[✓] Transacción completada con éxito
[✓] Integridad verificada (MAC válido)

Saldo transferido: 500.00 EUR
```

---

## 🧪 Testing

### Ejecutar todos los tests

```bash
pytest tests/ -v
```

### Ejecutar tests específicos

```bash
# Tests de MAC
pytest tests/test_mac.py -v

# Tests de NONCE (anti-replay)
pytest tests/test_nonce.py -v

# Tests de Argon2
pytest tests/test_argon2.py -v

# Tests de timing attacks
pytest tests/test_timing.py -v

# Tests de integración completa
pytest tests/test_integration.py -v
```

### Salida esperada

```
tests/test_mac.py::test_generar_mac ✓
tests/test_mac.py::test_verificar_mac_valido ✓
tests/test_mac.py::test_verificar_mac_invalido ✓
tests/test_nonce.py::test_generar_nonce_unico ✓
tests/test_nonce.py::test_detectar_replay ✓
tests/test_argon2.py::test_hash_password ✓
tests/test_argon2.py::test_verify_password ✓
tests/test_timing.py::test_constant_time_comparison ✓
tests/test_integration.py::test_flujo_completo ✓

======================== 9 passed in 2.34s ========================
```

---

## 📊 Logs de Evidencias

### Revisar logs en tiempo real

```bash
# Log del servidor
tail -f logs/servidor.log

# Log de transacciones
tail -f logs/transacciones.log

# Log de seguridad (ataques detectados)
tail -f logs/seguridad.log
```

### Ejemplo de log del servidor

```
2025-02-20 10:15:23 - INFO - Servidor iniciado en puerto 5000
2025-02-20 10:15:45 - INFO - Cliente conectado desde 127.0.0.1:54321
2025-02-20 10:15:47 - INFO - Registro exitoso: usuario 'juan'
2025-02-20 10:16:12 - INFO - Login exitoso: usuario 'juan'
2025-02-20 10:16:30 - INFO - Transacción verificada (MAC OK): juan → 500.00€
2025-02-20 10:16:31 - INFO - NONCE usado y registrado: a3f5b2c8...
2025-02-20 10:17:45 - WARNING - Intento de replay detectado! NONCE duplicado
2025-02-20 10:17:46 - ERROR - MAC inválido - Posible ataque MiTM
```

---

## 🛡️ Protecciones Implementadas

| Ataque | Mecanismo de Protección | Implementación |
|--------|------------------------|----------------|
| **Man-in-the-Middle** | HMAC-SHA256 | MAC detecta cualquier modificación del mensaje |
| **Replay** | NONCE único | Servidor rechaza NONCEs ya utilizados |
| **Key Derivation** | Argon2id | Salt único por usuario + alta complejidad |
| **Timing Attacks** | Constant-time comparison | `hmac.compare_digest()` en todas las comparaciones |
| **Brute Force** | Argon2id | Parámetros robustos (time_cost=3, memory=64MB) |

---

## 📦 Entregable Final

### Crear el archivo ZIP

```bash
# Desde el directorio raíz del proyecto
zip -r PAI1-STX.zip . -x "*.db" "*.key" ".env" "__pycache__/*" "venv/*" "*.pyc"
```

### Contenido del ZIP

El archivo `PAI1-STX.zip` debe contener:

✅ **Código fuente completo**
- `cliente/`, `servidor/`, `common/`, `tests/`

✅ **Scripts y configuración**
- `database/`, `scripts/`, `config/` (sin archivos .key)
- `requirements.txt`, `.env.example`, `.gitignore`

✅ **Logs de evidencias**
- `logs/` con registros de pruebas reales

✅ **Documentación**
- `docs/Manual_PAI1.pdf` (máximo 10 páginas)
- `README.md`

✅ **Scripts de ejecución**
- `run_servidor.py`, `run_cliente.py`

❌ **NO incluir:**
- Archivos `.key` (clave compartida)
- Base de datos con datos reales (`.db`)
- Carpetas `__pycache__` o `venv/`
- Archivo `.env` con secretos

---

## 📈 Estadísticas del Proyecto

| Componente | Líneas de Código (aprox.) |
|-----------|---------------------------|
| `cliente_cli.py` | ~200 líneas |
| `crypto_client.py` | ~150 líneas |
| `comunicacion.py` | ~100 líneas |
| `servidor.py` | ~250 líneas |
| `autenticacion.py` | ~180 líneas |
| `crypto_server.py` | ~150 líneas |
| `database.py` | ~200 líneas |
| `protocolo.py` | ~80 líneas |
| `config.py` | ~50 líneas |
| `tests/*.py` | ~100-150 c/u |
| **TOTAL** | **~1,500-2,000 líneas** |

---

## 👥 Equipo de Desarrollo

**Security Team X (STX)**

Universidad de Sevilla - E.T.S. Ingeniería Informática  
Asignatura: Ingeniería de Seguridad  
Proyecto: PAI1 - INTEGRIDOS

---

## 📝 Licencia

Este proyecto es parte de un trabajo académico para la Universidad de Sevilla.

---

## 📞 Contacto y Soporte

Para dudas o consultas sobre el proyecto:
- **Repositorio:** [GitHub/PAI1-INTEGRIDOS]
- **Email:** [tu-email@alum.us.es]

---

## 🎯 Fecha de Entrega

**Deadline:** 20 de febrero de 2025 a las 23:59 horas

⚠️ **Importante:** Los proyectos entregados fuera de plazo tendrán una penalización del 10% por cada día de retraso.

---

**¡Buena suerte con el proyecto!** 🚀