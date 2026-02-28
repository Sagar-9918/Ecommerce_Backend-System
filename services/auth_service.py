"""
services/auth_service.py
────────────────────────
Authentication business logic — registration, login, token refresh.
"""

from models.user import User
from utils.jwt_handler import generate_access_token, generate_refresh_token, decode_token
import jwt


class AuthService:
    """Handles all authentication-related business logic."""

    @staticmethod
    def register(name: str, email: str, password: str) -> dict:
        """Register a new customer account."""

        # Validation
        if not all([name, email, password]):
            raise ValueError("Name, email and password are required")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        if "@" not in email:
            raise ValueError("Invalid email format")
        if User.email_exists(email):
            raise ValueError("Email is already registered")

        user_id = User.create(name, email.lower().strip(), password)
        user    = User.find_by_id(user_id)

        return {
            "user":          user.to_dict(),
            "access_token":  generate_access_token(user.id, user.role),
            "refresh_token": generate_refresh_token(user.id),
            "token_type":    "Bearer"
        }

    @staticmethod
    def login(email: str, password: str) -> dict:
        """Validate credentials and return tokens."""
        if not email or not password:
            raise ValueError("Email and password are required")

        user = User.find_by_email(email.lower().strip())
        if not user:
            raise ValueError("Invalid email or password")
        if not User.verify_password(password, user.password):
            raise ValueError("Invalid email or password")

        return {
            "user":          user.to_dict(),
            "access_token":  generate_access_token(user.id, user.role),
            "refresh_token": generate_refresh_token(user.id),
            "token_type":    "Bearer"
        }

    @staticmethod
    def refresh_tokens(refresh_token: str) -> dict:
        """Issue new access token using a valid refresh token."""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Not a refresh token")

            user = User.find_by_id(payload["sub"])
            if not user:
                raise ValueError("User not found")

            return {
                "access_token": generate_access_token(user.id, user.role),
                "token_type":   "Bearer"
            }
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token has expired, please login again")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid refresh token")

    @staticmethod
    def get_profile(user_id: int) -> dict:
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user.to_dict()

    @staticmethod
    def update_profile(user_id: int, name: str) -> dict:
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        user.update_profile(name)
        return user.to_dict()

    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str):
        user = User.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if not User.verify_password(current_password, user.password):
            raise ValueError("Current password is incorrect")
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters")
        user.change_password(new_password)
