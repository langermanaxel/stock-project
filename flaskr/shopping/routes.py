from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flaskr.security import roles_required
from flaskr.db import get_db

bp = Blueprint("shopping", __name__, url_prefix="/shopping")

@bp.get("/list")
@roles_required("ADMIN")
def list():
    """
    Listado de compras registradas (solo ADMIN).
    Muestra producto, cantidad, precio, total, usuario y fecha.
    """
    db = get_db()

    compras = db.execute("""
        SELECT 
            s.id,
            p.name AS product_name,
            s.quantity,
            s.unit_price,
            s.total_price,
            s.purchase_date,
            u.username AS created_by
        FROM shopping AS s
        JOIN product AS p ON s.product_id = p.id
        LEFT JOIN user AS u ON s.created_by = u.id
        ORDER BY s.purchase_date DESC;
    """).fetchall()

    return render_template("shopping/list.html", compras=compras)

@bp.get("/my")
@roles_required("USER", "ADMIN")
def my_purchases():
    """Muestra solo las compras registradas por el usuario actual."""
    db = get_db()
    compras = db.execute("""
        SELECT 
            s.id, p.name AS product_name, s.quantity, s.unit_price, s.total_price, s.purchase_date
        FROM shopping AS s
        JOIN product AS p ON s.product_id = p.id
        WHERE s.created_by = ?
        ORDER BY s.purchase_date DESC;
    """, (g.user["id"],)).fetchall()
    return render_template("shopping/my_list.html", compras=compras)

@bp.route("/new", methods=["GET", "POST"])
@roles_required("ADMIN")
def new():
    """Permite al ADMIN registrar una compra."""
    db = get_db()
    productos = db.execute("SELECT id, name FROM product ORDER BY name").fetchall()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity = int(request.form.get("quantity", 0))
        unit_price = float(request.form.get("unit_price", 0))

        if not product_id or quantity <= 0 or unit_price <= 0:
            flash("⚠️ Datos inválidos. Verificá los campos.", "warning")
        else:
            db.execute("""
                INSERT INTO shopping (product_id, quantity, unit_price, created_by)
                VALUES (?, ?, ?, ?)
            """, (product_id, quantity, unit_price, g.user["id"]))
            db.commit()
            flash("✅ Compra registrada y stock actualizado.", "success")
            return redirect(url_for("shopping.list"))

    return render_template("shopping/form.html", productos=productos, mode="new")