"""Authentication-related decorators."""

from functools import wraps

from flask import flash, redirect, url_for, abort, make_response
from flask_login import login_required, current_user


def admin_required(f):
    """Allow access only to admin users."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != "Admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("main_bp.index"))
        return f(*args, **kwargs)

    return decorated_function


def roles_required(*roles):
    """Ensure the current user has one of the given roles."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                return abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def nocache(view):
    """Disable caching for a route."""

    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return no_cache