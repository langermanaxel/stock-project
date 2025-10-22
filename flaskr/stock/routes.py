from flask import Blueprint, render_template, request, redirect, url_for, flash
from flaskr.security import roles_required
from flaskr.db import get_db

bp = Blueprint("stock", __name__, url_prefix="/stock")

# 🧾 1️⃣ Vista de CONSULTA (para USER y ADMIN)
@bp.route('/consult', methods=('GET', 'POST'))
@roles_required('USER', 'ADMIN')
def consult():
    """
    Vista para consultar productos (USER o ADMIN)
    - El usuario tipo USER solo puede ver el stock y precios.
    - El ADMIN también puede acceder, pero para acciones avanzadas usa /list.
    """
    db = get_db()
    productos = db.execute(
        "SELECT id, name, category, current_stock, sale_price "
        "FROM product ORDER BY name"
    ).fetchall()
    return render_template('stock/consult.html', productos=productos)


# 🧩 2️⃣ Vista de LISTADO COMPLETO (solo ADMIN)
@bp.get("/list")
@roles_required("ADMIN")
def list():
    """
    Panel completo de gestión de stock (solo ADMIN)
    Permite ver, editar y eliminar productos.
    """
    db = get_db()
    productos = db.execute(
        "SELECT id, name, category, current_stock, sale_price, purchase_price "
        "FROM product ORDER BY name"
    ).fetchall()
    return render_template("stock/list.html", productos=productos)


@bp.route("/new", methods=["GET", "POST"])
@roles_required("ADMIN")
def create():
    """Permite al ADMIN crear un nuevo producto."""
    if request.method == "POST":
        name = request.form["name"].strip()
        category = request.form.get("category", "").strip()
        current_stock = int(request.form.get("current_stock", "0") or 0)
        sale_price = float(request.form.get("sale_price", "0") or 0)
        purchase_price = float(request.form.get("purchase_price", "0") or 0)

        db = get_db()
        db.execute(
            """
            INSERT INTO product (name, category, current_stock, sale_price, purchase_price)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, category, current_stock, sale_price, purchase_price),
        )
        db.commit()

        flash("✅ Producto creado con éxito.", "success")
        return redirect(url_for("stock.list"))

    return render_template("stock/form.html", mode="new")


# ✏️ Editar producto
@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@roles_required("ADMIN")
def edit(id):
    db = get_db()
    producto = db.execute("SELECT * FROM product WHERE id = ?", (id,)).fetchone()

    if producto is None:
        flash("❌ Producto no encontrado.", "error")
        return redirect(url_for("stock.list"))

    if request.method == "POST":
        nombre = request.form["name"].strip()
        categoria = request.form.get("category", "").strip()
        precio_compra = float(request.form.get("sale_price", "0") or 0)
        precio_venta = float(request.form.get("purchase_price", "0") or 0)

        db.execute("""
            UPDATE product
            SET name = ?, category = ?, sale_price = ?, purchase_price = ?
            WHERE id = ?
        """, (nombre, categoria, precio_compra, precio_venta, id))
        db.commit()

        flash("✅ Producto actualizado.", "success")
        return redirect(url_for("stock.list"))

    return render_template("stock/form.html", producto=producto, mode="edit")


# 🗑️ Eliminar producto
@bp.route("/delete/<int:id>", methods=["GET", "POST"])
@roles_required("ADMIN")
def delete(id):
    db = get_db()
    producto = db.execute("SELECT * FROM product WHERE id = ?", (id,)).fetchone()

    if producto is None:
        flash("❌ Producto no encontrado.", "error")
        return redirect(url_for("stock.list"))

    if request.method == "POST":
        db.execute("DELETE FROM product WHERE id = ?", (id,))
        db.commit()
        flash("🗑️ Producto eliminado correctamente.", "success")
        return redirect(url_for("stock.list"))

    return render_template("stock/delete.html", producto=producto)
