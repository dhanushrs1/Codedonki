"""
JWT auth helpers shared across blueprints.
"""
import os
import jwt
import functools
from flask import request, jsonify


def get_jwt_secret():
    return os.getenv("JWT_SECRET_KEY", "changeme-jwt-secret")


def get_jwt_identity():
    """Helper to get identity from JWT in the 'Authorization' header."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, "Missing Authorization header"
    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return None, "Invalid Authorization header format"
    token = parts[1]
    try:
        identity = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
        return identity, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


def admin_required(f):
    """Decorator to protect routes that require 'admin' role."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        identity, error = get_jwt_identity()
        if not identity:
            return jsonify({"error": error}), 401
        if identity.get('role') != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    """Decorator to protect routes that require any logged-in user."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        identity, error = get_jwt_identity()
        if not identity:
            return jsonify({"error": error}), 401
        request.current_user = identity
        return f(*args, **kwargs)
    return decorated_function
