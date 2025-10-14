from flask import Blueprint, render_template
from flaskr.security import roles_required
from flaskr.db import get_db

bp = Blueprint("sales", __name__, url_prefix="/sales")

@bp.route('/carry', methods=('GET', 'POST'))
@roles_required('USER', 'ADMIN')
def carry():
    # lógica para registrar venta
    return render_template('sales/carry.html')

@bp.route("/list")
@roles_required("ADMIN", "USER")
def list():
    """Página de listado de ventas."""
    db = get_db()
    ventas = db.execute("SELECT * FROM ventas ORDER BY id DESC").fetchall() if db else []
    return render_template("sales/list.html", ventas=ventas)