import sqlite3
from flask import Blueprint, flash, redirect, render_template, request, url_for, session, g
import functools
from werkzeug.security import generate_password_hash, check_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

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

        # Validaciones del lado servidor (siempre necesarias)
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
                db.execute(
                    """
                    INSERT INTO user (firstname, lastname, email, username, password_hash)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (firstname, lastname, email, username, generate_password_hash(password)),
                )
                db.commit()
            except sqlite3.IntegrityError as e:
                # Distinguir violaciones de UNIQUE por columna
                msg = str(e)
                if 'user.username' in msg:
                    error = 'Ese nombre de usuario ya está en uso.'
                elif 'user.email' in msg:
                    error = 'Ese correo ya está registrado.'
                else:
                    error = 'No se pudo completar el registro.'
            else:
                flash('Cuenta creada correctamente. Ahora podés iniciar sesión.', 'success')
                return redirect(url_for('auth.login'))

        flash(error, 'error')

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # Normalizar entradas
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''

        error = None
        if not username or not password:
            error = 'Ingresá tu usuario y contraseña.'
        else:
            db = get_db()
            # Si querés case-insensitive para username, podés agregar "COLLATE NOCASE" en la consulta
            user = db.execute(
                'SELECT * FROM user WHERE username = ?',
                (username,)
            ).fetchone()

            if user is None or not check_password_hash(user['password_hash'], password):
                # Mensaje genérico para no revelar si el usuario existe
                error = 'Usuario o contraseña incorrectos.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            # Redirigir a una vista real (por ejemplo, home del app)
            return redirect(url_for('main.index'))  # ajustá al endpoint que quieras

        flash(error, 'error')

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))  # ajustá al endpoint post-logout


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view