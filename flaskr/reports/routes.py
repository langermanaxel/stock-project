from flask import Blueprint, render_template
from flaskr.db import get_db
from flaskr.security import roles_required

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.get("/")
@roles_required("ADMIN")
def index():
    db = get_db()

    # 💰 Ventas totales del día actual
    ventas_hoy = db.execute("""
        SELECT COALESCE(SUM(total_price), 0) AS total
        FROM sales
        WHERE DATE(sale_date) = DATE('now')
    """).fetchone()["total"]

    # 🏆 Top 5 productos más vendidos (por cantidad)
    top5 = db.execute("""
        SELECT p.name AS product_name, SUM(s.quantity) AS total_sold
        FROM sales s
        JOIN product p ON s.product_id = p.id
        GROUP BY p.id
        ORDER BY total_sold DESC
        LIMIT 5
    """).fetchall()

    # 📈 Total de compras del día (opcional)
    compras_hoy = db.execute("""
        SELECT COALESCE(SUM(total_price), 0) AS total
        FROM shopping
        WHERE DATE(purchase_date) = DATE('now')
    """).fetchone()["total"]

    return render_template(
        "reports/index.html",
        ventas_hoy=ventas_hoy,
        compras_hoy=compras_hoy,
        top5=top5
    )
