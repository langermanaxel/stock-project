# flaskr/db.py
import os
import sqlite3
from datetime import datetime
import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


# ---------------------------------
# Conexión e inicialización básica
# ---------------------------------
def _connect_db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(
        path,
        detect_types=sqlite3.PARSE_DECLTYPES,
        timeout=10.0,            # evita "database is locked"
        check_same_thread=False  # útil si hay threads/WSGI
    )
    conn.row_factory = sqlite3.Row

    # PRAGMAs recomendados para SQLite en apps web
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = _connect_db(current_app.config["DATABASE"])
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    db.commit()


# -----------------
# Comandos de CLI
# -----------------
@click.command("init-db")
def init_db_command():
    """Recrea la base de datos a partir de schema.sql (sin datos seed)."""
    init_db()
    click.echo("Initialized the database.")


@click.command("create-admin")
@click.option("--email", prompt=True)
@click.option("--username", prompt=True)
@click.option("--firstname", prompt=True, default="Admin")
@click.option("--lastname", prompt=True, default="Root")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def create_admin_command(email, username, firstname, lastname, password):
    """
    Crea o actualiza un usuario ADMIN (upsert por email).
    Requiere que schema.sql ya haya sido aplicado (init-db).
    """
    if len(password) < 8:
        click.echo("La contraseña debe tener al menos 8 caracteres.")
        raise SystemExit(1)

    email = (email or "").strip().lower()
    username = (username or "").strip()
    firstname = (firstname or "").strip()
    lastname = (lastname or "").strip()

    if not email or not username or not firstname or not lastname:
        click.echo("Todos los campos son obligatorios.")
        raise SystemExit(1)

    db = get_db()
    password_hash = generate_password_hash(password)

    db.execute(
        """
        INSERT INTO user (firstname, lastname, email, username, password_hash, role)
        VALUES (?, ?, ?, ?, ?, 'ADMIN')
        ON CONFLICT(email) DO UPDATE SET
            username=excluded.username,
            firstname=excluded.firstname,
            lastname=excluded.lastname,
            password_hash=excluded.password_hash,
            role='ADMIN';
        """,
        (firstname, lastname, email, username, password_hash),
    )
    db.commit()
    click.echo(f"Admin listo: {email} (username: {username})")


# -----------------
# Converters (opcional)
# -----------------
sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)

    # 🚀 Inicialización automática en Render (Flask 3.x compatible)
    with app.app_context():
        db_path = app.config["DATABASE"]
        if not os.path.exists(db_path):
            try:
                from flaskr.db import init_db
                init_db()
                print("🗄️ Base de datos inicializada automáticamente en Render (Flask 3.x).")
            except Exception as e:
                print(f"⚠️ Error al inicializar la base de datos: {e}")

