import os
from datetime import timedelta
from flask import Flask, redirect, url_for, render_template
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_mail import Mail

mail = Mail()
csrf = CSRFProtect()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.config.update(
        # Sesión
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,          # ⚠️ ponelo en True en PROD con HTTPS
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),

        # Tokens (itsdangerous)
        SECURITY_PASSWORD_SALT=os.getenv('SECURITY_PASSWORD_SALT', 'otra-sal-separada'),

        # Email (Gmail SMTP + App Password)
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,                    # TLS en 587
        MAIL_USE_SSL=False,           # explícito para no mezclar
        MAIL_SUPPRESS_SEND=False,     # asegúrate de que no esté True
        MAIL_DEBUG=True,              # ver mensajes SMTP en consola
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=("StockApp", os.getenv('MAIL_USERNAME')),

        # CSRF (Flask-WTF)
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_TIME_LIMIT=60*60*2,
        WTF_CSRF_SSL_STRICT=False,
    )

    mail.init_app(app)
    csrf.init_app(app)

    from . import db
    db.init_app(app)

    from . import auth, index, validate, users, sales, stock
    app.register_blueprint(auth.bp)
    app.register_blueprint(index.bp)
    app.register_blueprint(validate.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(sales.bp)
    app.register_blueprint(stock.bp)

    app.add_url_rule("/", endpoint="root",
                     view_func=lambda: redirect(url_for("auth.login")))

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return (render_template("errors/csrf.html", reason=e.description), 400)

    return app
