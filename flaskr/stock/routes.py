from flask import Blueprint, render_template
from flaskr.security import login_required, roles_required

bp = Blueprint("stock", __name__, url_prefix="/stock")

@bp.route('/consult', methods=('GET', 'POST'))
@roles_required('USER', 'ADMIN')
def consult():
    # lógica para registrar venta
    return render_template('stock/consult.html')
