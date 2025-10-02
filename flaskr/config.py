app.config.update(
    SECRET_KEY="cambia-esto-por-uno-seguro",   # requerido para firmar las cookies
    SESSION_COOKIE_HTTPONLY=True,              # la cookie no es accesible por JS
    SESSION_COOKIE_SECURE=True,                # solo en HTTPS (dejalo False si estás en local sin SSL)
    SESSION_COOKIE_SAMESITE="Lax",             # o "Strict" si no hacés requests cross-site
    PERMANENT_SESSION_LIFETIME=60*60*24*7      # ejemplo: 7 días
)