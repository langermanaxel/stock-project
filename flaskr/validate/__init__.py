# flaskr/validate/__init__.py
from flask import Blueprint

bp = Blueprint("validate", __name__, url_prefix="/validate")

# Importa las rutas para que se registren en el blueprint
from . import routes_reset  # noqa: E402,F401
