import os
from datetime import timedelta
from dotenv import load_dotenv

# Load values from .env file
load_dotenv()

class Config:
    """Base configuration — values loaded from .env file."""

    # ── Flask ──────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    DEBUG      = False

    # ── MySQL ──────────────────────────────────────────────────
    DB_HOST     = os.getenv("DB_HOST",     "localhost")
    DB_PORT     = int(os.getenv("DB_PORT", "3306"))
    DB_USER     = os.getenv("DB_USER",     "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME     = os.getenv("DB_NAME",     "ecommerce_db")

    # ── JWT ────────────────────────────────────────────────────
    JWT_SECRET_KEY     = os.getenv("JWT_SECRET_KEY", "change-this-jwt-key")
    JWT_ACCESS_EXPIRY  = timedelta(hours=1)
    JWT_REFRESH_EXPIRY = timedelta(days=7)

    # ── Pagination ─────────────────────────────────────────────
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE     = 100


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Active config
config = DevelopmentConfig()
