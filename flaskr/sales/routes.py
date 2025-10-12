from flask import Blueprint, render_template
from flaskr.security import login_required, roles_required

bp = Blueprint("sales", __name__, url_prefix="/sales")

@bp.route('/carry', methods=('GET', 'POST'))
@roles_required('USER', 'ADMIN')
def carry():
    # lógica para registrar venta
    return render_template('sales/carry.html')
