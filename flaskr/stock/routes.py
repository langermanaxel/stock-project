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
        "SELECT id, nombre, categoria, stock_actual, precio_venta "
        "FROM producto ORDER BY nombre"
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
        "SELECT id, nombre, categoria, stock_actual, precio_venta, precio_compra "
        "FROM producto ORDER BY nombre"
    ).fetchall()
    return render_template("stock/list.html", productos=productos)


# ➕ 3️⃣ Crear nuevo producto (solo ADMIN)
@bp.route("/new", methods=["GET", "POST"])
@roles_required("ADMIN")
def create():
    """
    Permite al ADMIN crear un nuevo producto.
    """
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        categoria = request.form.get("categoria", "").strip()
        precio_venta = float(request.form.get("precio_venta", "0") or 0)
        precio_compra = float(request.form.get("precio_compra", "0") or 0)

        db = get_db()
        db.execute(
            "INSERT INTO products (nombre, categoria, stock_actual, precio_compra, precio_venta) "
            "VALUES (?, ?, ?, ?, ?)",
            (nombre, categoria, 0, precio_compra, precio_venta),
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
    producto = db.execute("SELECT * FROM producto WHERE id = ?", (id,)).fetchone()

    if producto is None:
        flash("❌ Producto no encontrado.", "error")
        return redirect(url_for("stock.list"))

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        categoria = request.form.get("categoria", "").strip()
        precio_compra = float(request.form.get("precio_compra", "0") or 0)
        precio_venta = float(request.form.get("precio_venta", "0") or 0)

        db.execute("""
            UPDATE products
            SET nombre = ?, categoria = ?, precio_compra = ?, precio_venta = ?
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
    producto = db.execute("SELECT * FROM producto WHERE id = ?", (id,)).fetchone()

    if producto is None:
        flash("❌ Producto no encontrado.", "error")
        return redirect(url_for("stock.list"))

    if request.method == "POST":
        db.execute("DELETE FROM products WHERE id = ?", (id,))
        db.commit()
        flash("🗑️ Producto eliminado correctamente.", "success")
        return redirect(url_for("stock.list"))

    return render_template("stock/delete.html", producto=producto)
