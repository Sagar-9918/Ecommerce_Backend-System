"""
models/user.py
──────────────
User model — OOP representation with class-level DB operations.
"""

import bcrypt
from utils.db import execute_query


class User:
    """Represents a user account in the system."""

    def __init__(self, id=None, name=None, email=None,
                 password=None, role="customer",
                 created_at=None, updated_at=None):
        self.id         = id
        self.name       = name
        self.email      = email
        self.password   = password
        self.role       = role
        self.created_at = created_at
        self.updated_at = updated_at

    # ── Serialisation ──────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a safe (no-password) dict representation."""
        return {
            "id":         self.id,
            "name":       self.name,
            "email":      self.email,
            "role":       self.role,
            "created_at": str(self.created_at) if self.created_at else None
        }

    # ── Password helpers ───────────────────────────────────────

    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    # ── DB operations ──────────────────────────────────────────

    @classmethod
    def find_by_email(cls, email: str):
        row = execute_query(
            "SELECT * FROM users WHERE email = %s", (email,), fetch="one"
        )
        return cls(**row) if row else None

    @classmethod
    def find_by_id(cls, user_id: int):
        row = execute_query(
            "SELECT * FROM users WHERE id = %s", (user_id,), fetch="one"
        )
        return cls(**row) if row else None

    @classmethod
    def create(cls, name: str, email: str, plain_password: str, role: str = "customer"):
        hashed = cls.hash_password(plain_password)
        result = execute_query(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed, role)
        )
        return result["lastrowid"]

    @classmethod
    def email_exists(cls, email: str) -> bool:
        row = execute_query(
            "SELECT id FROM users WHERE email = %s", (email,), fetch="one"
        )
        return row is not None

    def update_profile(self, name: str = None):
        if name:
            self.name = name
            execute_query(
                "UPDATE users SET name = %s WHERE id = %s",
                (self.name, self.id)
            )

    def change_password(self, new_plain: str):
        self.password = self.hash_password(new_plain)
        execute_query(
            "UPDATE users SET password = %s WHERE id = %s",
            (self.password, self.id)
        )
