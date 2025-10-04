# app/auth/routes_reset.py
from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from . import bp
from ..db import get_db  # adapta a como obtienes la conexión
from .tokens import generate_reset_token, verify_reset_token
from flask_mail import Message
from .. import mail  # importado desde __init__.py donde hiciste mail = Mail()

def _find_user_by_email(db, email: str):
    return db.execute("SELECT id, email FROM user WHERE email = ?", (email,)).fetchone()

def _update_user_password(db, user_id: int, pwd_hash: str):
    db.execute("UPDATE user SET password = ? WHERE id = ?", (pwd_hash, user_id))
    db.commit()

@bp.get("/forgot")
def forgot_password_form():
    return render_template("auth/forgot_password.html")

@bp.post("/forgot")
def forgot_password_submit():
    email = request.form.get("email", "").strip().lower()
    db = get_db()
    user = _find_user_by_email(db, email)

    # Mensaje genérico SIEMPRE (no revelar existencia)
    flash("Si el email está registrado, te enviamos instrucciones.", "info")

    if user:
        token = generate_reset_token(user["id"])
        reset_url = url_for("validate.reset_password_form", token=token, _external=True)

        # Opción A: enviar email real
        try:
            msg = Message(subject="Restablecer contraseña",
                          recipients=[email],
                          body=f"Para restablecer tu contraseña, hacé clic: {reset_url}\n\nEste enlace expira en 1 hora.")
            mail.send(msg)
        except Exception:
            # Opción B: en desarrollo, registrá el link en logs o consola
            print("LINK DE RECUPERACIÓN:", reset_url)

    return redirect(url_for("auth.login"))  # o mostrar una página de confirmación

@bp.get("/reset/<token>")
def reset_password_form(token):
    user_id = verify_reset_token(token)
    if not user_id:
        flash("El enlace no es válido o expiró.", "warning")
        return redirect(url_for("auth.forgot_password_form"))
    return render_template("auth/reset_password.html", token=token)

@bp.post("/reset/<token>")
def reset_password_submit(token):
    user_id = verify_reset_token(token)
    if not user_id:
        flash("El enlace no es válido o expiró.", "warning")
        return redirect(url_for("validate.forgot_password_form"))

    pwd = request.form.get("password", "")
    pwd2 = request.form.get("password2", "")

    # Validaciones mínimas
    if len(pwd) < 8 or pwd != pwd2:
        flash("La contraseña debe tener al menos 8 caracteres y coincidir.", "danger")
        return redirect(url_for("validate.reset_password_form", token=token))

    pwd_hash = generate_password_hash(pwd)
    db = get_db()
    _update_user_password(db, user_id, pwd_hash)

    flash("Tu contraseña fue actualizada. Ya podés iniciar sesión.", "success")
    return redirect(url_for("auth.login"))
