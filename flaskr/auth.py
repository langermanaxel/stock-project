import sqlite3
import functools
from flask import (
    Blueprint, flash, redirect, render_template,
    request, url_for, session, g
)
from werkzeug.security import generate_password_hash, check_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# ----------------------------
# Helpers / Decoradores
# ----------------------------
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Tenés que iniciar sesión.', 'error')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def roles_required(*roles):
    """
    Restringe el acceso a usuarios cuyo g.user['role'] esté en `roles`.
    Uso:
        @roles_required('ADMIN')
        @roles_required('USER', 'ADMIN')
    """
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                flash('Tenés que iniciar sesión.', 'error')
                return redirect(url_for('auth.login'))
            if g.user['role'] not in roles:
                flash('Acceso denegado.', 'error')
                # Cambiá 'main.index' por la home real de tu app
                return redirect(url_for('main.index'))
            return view(**kwargs)
        return wrapped_view
    return decorator


from flask import g, session
from flaskr.db import get_db

@bp.before_app_request
def load_logged_in_user():
    """Carga g.user desde la sesión si hay user_id. Tolerante a errores."""
    user_id = session.get("user_id")

    # Si no hay sesión activa, g.user = None
    if user_id is None:
        g.user = None
        return

    try:
        db = get_db()
        row = db.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        g.user = dict(row) if row else None
    except Exception as e:
        # Previene que errores de DB rompan la sesión
        g.user = None




# ----------------------------
# Registro
# ----------------------------
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # Normalizar y extraer campos
        firstname = (request.form.get('firstname') or '').strip()
        lastname = (request.form.get('lastname') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''

        error = None

        # Validaciones del lado servidor
        if not all([firstname, lastname, email, username, password, confirm_password]):
            error = 'Todos los campos son obligatorios.'
        elif len(password) < 8:
            error = 'La contraseña debe tener al menos 8 caracteres.'
        elif password != confirm_password:
            error = 'Las contraseñas no coinciden.'
        elif '@' not in email or '.' not in email.split('@')[-1]:
            error = 'El correo electrónico no parece válido.'

        if error is None:
            db = get_db()
            try:
                # Importante: NO permitimos fijar role desde el form público.
                # Queda en DEFAULT 'USER' definido en el schema.
                db.execute(
                    """
                    INSERT INTO user (firstname, lastname, email, username, password_hash)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (firstname, lastname, email, username, generate_password_hash(password)),
                )
                db.commit()
            except sqlite3.IntegrityError as e:
                # Manejo robusto de UNIQUE
                msg = str(e)
                if 'user.username' in msg or 'UNIQUE constraint failed: user.username' in msg:
                    error = 'Ese nombre de usuario ya está en uso.'
                elif 'user.email' in msg or 'UNIQUE constraint failed: user.email' in msg:
                    error = 'Ese correo ya está registrado.'
                else:
                    error = 'No se pudo completar el registro.'
            else:
                flash('Cuenta creada correctamente. Ahora podés iniciar sesión.', 'success')
                return redirect(url_for('auth.login'))

        flash(error, 'error')

    return render_template('auth/register.html')


# ----------------------------
# Login
# ----------------------------
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''

        error = None
        user = None

        if not username or not password:
            error = 'Ingresá tu usuario y contraseña.'
        else:
            db = get_db()
            # Búsqueda case-insensitive (si el schema no tiene COLLATE NOCASE en username, esto lo cubre)
            user = db.execute(
                "SELECT * FROM user WHERE username = ? COLLATE NOCASE",
                (username,)
            ).fetchone()

            # Mensaje genérico para no filtrar existencia del usuario
            if user is None or not check_password_hash(user['password_hash'], password):
                error = 'Usuario o contraseña incorrectos.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']

            # Guardar último acceso
            db = get_db()
            db.execute(
                "UPDATE user SET last_login_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = ?",
                (user['id'],)
            )
            db.commit()

            # Redirección opcional según rol
            if user['role'] == 'ADMIN':
                # Cambiá 'users.admin_panel' si tu endpoint difiere
                return redirect(url_for('users.admin_panel'))
            # Cambiá 'main.index' por el dashboard/home real
            return redirect(url_for('main.index'))

        flash(error, 'error')

    return render_template('auth/login.html')


# ----------------------------
# Logout
# ----------------------------
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
