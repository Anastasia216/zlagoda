from functools import wraps
from flask import session, redirect

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_role = session.get("role")

            if user_role not in roles:
                return "Access denied", 403

            return f(*args, **kwargs)

        return wrapper
    return decorator