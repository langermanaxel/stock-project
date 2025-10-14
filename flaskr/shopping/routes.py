from flask import Blueprint, render_template
from flaskr.security import roles_required
from flaskr.db import get_db

bp = Blueprint("shopping", __name__, url_prefix="/shopping")

@bp.get("/list")
@roles_required("ADMIN")
def list():
    """Listado de compras"""
    db = get_db()
    compras = db.execute("""
        SELECT id, proveedor, fecha, total
        FROM compra
        ORDER BY fecha DESC
    """).fetchall() if db else []
    return render_template("shopping/list.html", compras=compras)