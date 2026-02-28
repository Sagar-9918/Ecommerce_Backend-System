"""
routes/auth_routes.py
─────────────────────
Authentication endpoints:
  POST /auth/register
  POST /auth/login
  POST /auth/refresh
  GET  /auth/profile
  PUT  /auth/profile
  PUT  /auth/change-password
"""

from flask import Blueprint, request
from services.auth_service  import AuthService
from utils.jwt_handler      import token_required
from utils.response         import success, error

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account."""
    data = request.get_json() or {}
    try:
        result = AuthService.register(
            name     = data.get("name", "").strip(),
            email    = data.get("email", "").strip(),
            password = data.get("password", "")
        )
        return success("Registration successful", result, status=201)
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        return error(f"Registration failed: {e}", 500)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and receive JWT tokens."""
    data = request.get_json() or {}
    try:
        result = AuthService.login(
            email    = data.get("email", ""),
            password = data.get("password", "")
        )
        return success("Login successful", result)
    except ValueError as e:
        return error(str(e), 401)
    except Exception as e:
        return error(f"Login failed: {e}", 500)


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    """Get a new access token using a refresh token."""
    data = request.get_json() or {}
    try:
        result = AuthService.refresh_tokens(data.get("refresh_token", ""))
        return success("Token refreshed", result)
    except ValueError as e:
        return error(str(e), 401)


@auth_bp.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    """Get authenticated user's profile."""
    try:
        user = AuthService.get_profile(current_user["id"])
        return success("Profile fetched", user)
    except ValueError as e:
        return error(str(e), 404)


@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile(current_user):
    """Update name."""
    data = request.get_json() or {}
    try:
        user = AuthService.update_profile(current_user["id"], data.get("name", ""))
        return success("Profile updated", user)
    except ValueError as e:
        return error(str(e), 400)


@auth_bp.route("/change-password", methods=["PUT"])
@token_required
def change_password(current_user):
    """Change password."""
    data = request.get_json() or {}
    try:
        AuthService.change_password(
            user_id          = current_user["id"],
            current_password = data.get("current_password", ""),
            new_password     = data.get("new_password", "")
        )
        return success("Password changed successfully")
    except ValueError as e:
        return error(str(e), 400)
