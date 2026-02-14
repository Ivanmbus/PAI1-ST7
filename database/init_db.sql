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