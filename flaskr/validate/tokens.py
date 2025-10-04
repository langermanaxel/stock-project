from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app

def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

def generate_reset_token(user_id: int) -> str:
    s = _serializer()
    salt = current_app.config.get("SECURITY_PASSWORD_SALT", "pwd-reset")
    return s.dumps({"uid": user_id}, salt=salt)

def verify_reset_token(token: str, max_age_seconds: int = 3600) -> int | None:
    s = _serializer()
    salt = current_app.config.get("SECURITY_PASSWORD_SALT", "pwd-reset")
    try:
        data = s.loads(token, salt=salt, max_age=max_age_seconds)
        return int(data["uid"])
    except (BadSignature, SignatureExpired, KeyError, ValueError):
        return None
