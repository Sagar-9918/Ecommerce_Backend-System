"""
utils/jwt_handler.py
────────────────────
JWT-based session handling — generates and validates access/refresh tokens.
"""

import jwt
from datetime import datetime, timezone
from functools import wraps
from flask import request, jsonify
from config import config


# ── Token generation ───────────────────────────────────────────────────────────

def generate_access_token(user_id: int, role: str) -> str:
    """Create a short-lived access token (1 hour)."""
    payload = {
        "sub":  user_id,
        "role": role,
        "type": "access",
        "iat":  datetime.now(timezone.utc),
        "exp":  datetime.now(timezone.utc) + config.JWT_ACCESS_EXPIRY,
    }
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user_id: int) -> str:
    """Create a long-lived refresh token (7 days)."""
    payload = {
        "sub":  user_id,
        "type": "refresh",
        "iat":  datetime.now(timezone.utc),
        "exp":  datetime.now(timezone.utc) + config.JWT_REFRESH_EXPIRY,
    }
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    """Decode and validate a JWT; raises jwt exceptions on failure."""
    return jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])


# ── Route decorators ───────────────────────────────────────────────────────────

def token_required(f):
    """
    Decorator — protects a route with JWT auth.
    Injects `current_user` dict {id, role} into the wrapped function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False,
                            "message": "Authorization header missing or malformed"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                raise jwt.InvalidTokenError("Not an access token")
            current_user = {"id": payload["sub"], "role": payload["role"]}
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"success": False, "message": f"Invalid token: {e}"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorator — same as token_required but also enforces admin role.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False,
                            "message": "Authorization header missing or malformed"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                raise jwt.InvalidTokenError("Not an access token")
            if payload.get("role") != "admin":
                return jsonify({"success": False,
                                "message": "Admin access required"}), 403
            current_user = {"id": payload["sub"], "role": payload["role"]}
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"success": False, "message": f"Invalid token: {e}"}), 401

        return f(current_user, *args, **kwargs)

    return decorated
