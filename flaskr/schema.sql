-- schema.sql (solo DDL)

DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  firstname      TEXT NOT NULL,
  lastname       TEXT NOT NULL,
  email          TEXT NOT NULL UNIQUE COLLATE NOCASE,
  username       TEXT UNIQUE NOT NULL COLLATE NOCASE,
  password_hash  TEXT NOT NULL CHECK (length(password_hash) >= 60),
  role           TEXT NOT NULL DEFAULT 'USER' CHECK (role IN ('USER','ADMIN')),
  status         TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','SUSPENDED')),
  created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  last_login_at  TEXT
);

CREATE INDEX IF NOT EXISTS idx_user_role ON user(role);
CREATE INDEX IF NOT EXISTS idx_user_username ON user(username);

-- Trigger de actualización de updated_at
-- Evita bucle: solo se ejecuta si updated_at no cambió en la operación original.
CREATE TRIGGER IF NOT EXISTS trg_user_updated_at
AFTER UPDATE ON user
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
  UPDATE user
     SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
   WHERE id = NEW.id;
END;

-- =====================================================
-- Tabla: producto
-- =====================================================

DROP TABLE IF EXISTS product;

CREATE TABLE product (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name            TEXT NOT NULL,
  category        TEXT,
  current_stock   INTEGER NOT NULL DEFAULT 0 CHECK (current_stock >= 0),
  sale_price      REAL NOT NULL CHECK (sale_price >= 0),
  purchase_price  REAL NOT NULL CHECK (purchase_price >= 0),
  created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Índices útiles para búsquedas
CREATE INDEX IF NOT EXISTS idx_product_name ON product(name);
CREATE INDEX IF NOT EXISTS idx_product_category ON product(category);

-- Trigger para mantener updated_at actualizado
CREATE TRIGGER IF NOT EXISTS trg_product_updated_at
AFTER UPDATE ON product
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
  UPDATE product
     SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
   WHERE id = NEW.id;
END;
