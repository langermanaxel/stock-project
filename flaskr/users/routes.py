from flask import Blueprint, render_template, request, redirect, url_for, flash
from flaskr.security import login_required, roles_required
from flaskr.db import get_db

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.get("/perfil")
@login_required
def perfil():
    return render_template('users/user.html')

@bp.get("/admin")
@roles_required("ADMIN")
def admin_panel():
    db = get_db()
    # Ejemplo de métricas rápidas (ajustá a tus tablas reales)
    total_users = db.execute("SELECT COUNT(*) AS c FROM user").fetchone()["c"]
    admins = db.execute("SELECT COUNT(*) AS c FROM user WHERE role='ADMIN'").fetchone()["c"]
    return render_template('users/admin.html', total_users=total_users, admins=admins)

# flaskr/users/routes.py (continuación)
@bp.get("/manage")
@roles_required("ADMIN")
def manage():
    users = get_db().execute("SELECT id, firstname, lastname, email, username, role, status FROM user ORDER BY id").fetchall()
    return render_template("users/manage.html", users=users)

@bp.post("/set-role/<int:user_id>")
@roles_required("ADMIN")
def set_role(user_id):
    role = request.form.get("role")
    if role not in ("USER", "ADMIN"):
        flash("Rol inválido", "error")
        return redirect(url_for("users.manage"))
    db = get_db()
    db.execute("UPDATE user SET role=? WHERE id=?", (role, user_id))
    db.commit()
    flash("Rol actualizado", "success")
    return redirect(url_for("users.manage"))

@bp.post("/toggle-status/<int:user_id>")
@roles_required("ADMIN")
def toggle_status(user_id):
    db = get_db()
    row = db.execute("SELECT status FROM user WHERE id=?", (user_id,)).fetchone()
    if not row:
        flash("Usuario inexistente", "error")
        return redirect(url_for("users.manage"))
    new_status = "SUSPENDED" if row["status"] == "ACTIVE" else "ACTIVE"
    db.execute("UPDATE user SET status=? WHERE id=?", (new_status, user_id))
    db.commit()
    flash(f"Estado cambiado a {new_status}", "success")
    return redirect(url_for("users.manage"))
