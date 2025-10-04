from functools import wraps
from flask import g, redirect, url_for, abort

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if getattr(g, "user", None) is None:
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if getattr(g, "user", None) is None:
                return redirect(url_for("auth.login"))
            if g.user.get("role") not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
