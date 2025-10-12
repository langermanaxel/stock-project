# flaskr/reports/routes.py
from flask import Blueprint, render_template
from flaskr.security import roles_required
from flaskr.db import get_db

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.get("/")
@roles_required("ADMIN")
def index():
    db = get_db()
    # Ejemplos (ajustar a tus tablas reales)
    ventas_hoy = db.execute("""
        SELECT COALESCE(SUM(total),0) AS m
        FROM venta
        WHERE date(created_at) = date('now')
    """).fetchone()["m"]
    top5 = db.execute("""
        SELECT p.nombre, SUM(vd.cantidad) AS cant
        FROM venta_det vd
        JOIN producto p ON p.id = vd.producto_id
        GROUP BY p.id
        ORDER BY cant DESC
        LIMIT 5
    """).fetchall()
    return render_template("reports/index.html", ventas_hoy=ventas_hoy, top5=top5)
