from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flaskr.security import roles_required
from flaskr.db import get_db

bp = Blueprint("sales", __name__, url_prefix="/sales")

# ➕ Registrar nueva venta (USER y ADMIN)
@bp.route("/new", methods=["GET", "POST"])
@roles_required("USER", "ADMIN")
def new():
    """Permite registrar una nueva venta."""
    db = get_db()
    productos = db.execute("SELECT id, name, sale_price, current_stock FROM product ORDER BY name").fetchall()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity = int(request.form.get("quantity", 0))
        unit_price = float(request.form.get("unit_price", 0))

        if not product_id or quantity <= 0:
            flash("⚠️ Ingresá una cantidad válida.", "warning")
        else:
            # Verificar stock disponible
            stock = db.execute("SELECT current_stock FROM product WHERE id = ?", (product_id,)).fetchone()
            if stock and stock["current_stock"] < quantity:
                flash("❌ Stock insuficiente.", "error")
            else:
                db.execute("""
                    INSERT INTO sales (product_id, quantity, unit_price, created_by)
                    VALUES (?, ?, ?, ?)
                """, (product_id, quantity, unit_price, g.user["id"]))
                db.commit()
                flash("✅ Venta registrada correctamente.", "success")
                return redirect(url_for("sales.my_sales"))

    return render_template("sales/form.html", productos=productos, mode="new")


# 📋 Listado general de ventas (solo ADMIN)
@bp.get("/list")
@roles_required("ADMIN")
def list_all():
    """Listado completo de ventas (solo ADMIN)."""
    db = get_db()
    ventas = db.execute("""
        SELECT v.id, p.name AS product_name, v.quantity, v.unit_price, 
               v.total_price, v.sale_date, u.username AS sold_by
        FROM sales v
        JOIN product p ON v.product_id = p.id
        JOIN user u ON v.created_by = u.id
        ORDER BY v.sale_date DESC
    """).fetchall()
    return render_template("sales/list.html", ventas=ventas)


# 👤 Ventas del usuario logueado
@bp.get("/my")
@roles_required("USER", "ADMIN")
def my_sales():
    """Muestra las ventas realizadas por el usuario actual."""
    db = get_db()
    ventas = db.execute("""
        SELECT v.id, p.name AS product_name, v.quantity, v.unit_price, 
               v.total_price, v.sale_date
        FROM sales v
        JOIN product p ON v.product_id = p.id
        WHERE v.created_by = ?
        ORDER BY v.sale_date DESC
    """, (g.user["id"],)).fetchall()
    return render_template("sales/my_list.html", ventas=ventas)