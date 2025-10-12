from flask import Blueprint, render_template, request, redirect, url_for, flash
from flaskr.security import roles_required
from flaskr.db import get_db

bp = Blueprint("stock", __name__, url_prefix="/stock")

@bp.route('/consult', methods=('GET', 'POST'))
@roles_required('USER', 'ADMIN')
def consult():
    # lógica para registrar venta
    return render_template('stock/consult.html')

@bp.get("/list")
@roles_required("ADMIN")
def list():
    rows = get_db().execute("SELECT id, nombre, categoria, stock_actual, precio_venta FROM producto ORDER BY nombre").fetchall()
    return render_template("stock/list.html", productos=rows)

@bp.route("/new", methods=["GET","POST"])
@roles_required("ADMIN")
def new():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        categoria = request.form.get("categoria","").strip()
        precio = float(request.form.get("precio_venta", "0") or 0)
        db = get_db()
        db.execute("INSERT INTO producto (nombre, categoria, stock_actual, precio_venta) VALUES (?,?,?,?)",
                   (nombre, categoria, 0, precio))
        db.commit()
        flash("Producto creado.", "success")
        return redirect(url_for("stock.list"))
    return render_template("stock/form.html", mode="new")