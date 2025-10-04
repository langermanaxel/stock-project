from flask import Blueprint, render_template
from flaskr.security import login_required, roles_required

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.get("/perfil")
@login_required
def perfil():
    return render_template('users/user.html')

@bp.get("/admin")
@roles_required("ADMIN")
def admin_panel():
    return render_template('users/admin.html')
