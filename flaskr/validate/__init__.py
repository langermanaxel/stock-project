# flaskr/auth/__init__.py
from flask import Blueprint

bp = Blueprint("validate", __name__, url_prefix="/validate")
