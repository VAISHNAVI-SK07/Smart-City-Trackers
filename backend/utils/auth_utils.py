from functools import wraps
from flask import session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain_password):
    """Turns a plain-text password into a secure hash for storage."""
    return generate_password_hash(plain_password)


def verify_password(plain_password, stored_hash):
    """Checks a login attempt's password against the stored hash."""
    return check_password_hash(stored_hash, plain_password)


def login_required(f):
    """
    Decorator: blocks access unless SOMEONE is logged in (citizen or admin).
    Put this on any route that requires authentication.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated


def role_required(role):
    """
    Decorator factory: blocks access unless the logged-in user's role
    (read from the SERVER-SIDE session, never from the request body)
    matches the required role.

    Usage:
        @role_required('admin')
        def some_admin_only_route(): ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required. Please log in.'}), 401
            if session.get('role') != role:
                return jsonify({'error': 'You do not have permission to perform this action.'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
