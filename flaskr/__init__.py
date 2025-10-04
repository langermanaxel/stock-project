# flaskr/__init__.py
import os
from datetime import timedelta
from flask import Flask, redirect, url_for, render_template
from flask_wtf.csrf import CSRFProtect, CSRFError   # ⬅️ nuevo
from flask_mail import Mail

mail = Mail()
csrf = CSRFProtect()  # ⬅️ instancia global

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Base
    app.config.from_mapping(
        SECRET_KEY='dev',  # se sobrescribe abajo/por instancia/ENV
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Endurecer sesión + CSRF
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', app.config['SECRET_KEY']),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,          # True en PROD con HTTPS
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),

        # Configuración de email
        SECURITY_PASSWORD_SALT = "otra-sal-separada" , # para tokens
        MAIL_SERVER = "smtp.gmail.com",
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
        MAIL_USERNAME = "solomonsilversmith@gmail.com",
        MAIL_PASSWORD = "Bitcoin123",
        MAIL_DEFAULT_SENDER = ("StockApp", "solomonsilversmith@gmail.com"),

        # Opciones CSRF (Flask-WTF)
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_TIME_LIMIT=60 * 60 * 2,      # 2 horas (opcional)
        WTF_CSRF_SSL_STRICT=False,            # True sólo si siempre HTTPS
    )

    # Inicializar email
    mail.init_app(app)
    # Inicializar CSRF
    csrf.init_app(app)

    # DB
    from . import db
    db.init_app(app)

    # Blueprints
    from . import auth, index
    app.register_blueprint(auth.bp)
    app.register_blueprint(index.bp)

    # Raíz -> login
    app.add_url_rule("/", endpoint="root",
                     view_func=lambda: redirect(url_for("auth.login")))

    # Manejo elegante de errores CSRF
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        # Podés usar flash y redirigir si preferís
        return (render_template("errors/csrf.html", reason=e.description), 400)

    return app
