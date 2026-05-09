"""
Flask Application Configuration
Supports Development, Testing, and Production environments
Uses SQLite — no separate database installation required.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# Base directory of the flask-backend folder
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    """Base configuration shared across all environments."""

    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY         = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY     = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 2592000))  # 30 days
    )
    JWT_TOKEN_LOCATION = ['headers', 'query_string']
    JWT_HEADER_NAME    = 'Authorization'
    JWT_HEADER_TYPE    = 'Bearer'
    # Query-string token lookup — iframes can't set Authorization headers,
    # so the editor's live preview passes the JWT as ?access_token=... .
    JWT_QUERY_STRING_NAME      = 'access_token'
    JWT_QUERY_STRING_VALUE_PREFIX = ''

    # ── Database (SQLite) ──────────────────────────────────────────────────────
    # Default: website_builder.db in the flask-backend directory
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "website_builder.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False   # Set True to log all SQL queries

    # ── Payments ──────────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY      = os.environ.get('STRIPE_SECRET_KEY', '')
    STRIPE_WEBHOOK_SECRET  = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

    # ── CORS ──────────────────────────────────────────────────────────────────
    FRONTEND_URL  = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    # CORS origins — comma-separated list. Defaults to FRONTEND_URL.
    # Set CORS_ORIGINS="https://foo.com,https://bar.com" to allow multiple.
    CORS_ORIGINS  = [
        o.strip()
        for o in os.environ.get(
            'CORS_ORIGINS',
            os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        ).split(',')
        if o.strip()
    ]

    # ── Misc ──────────────────────────────────────────────────────────────────
    DEBUG               = False
    TESTING             = False
    MAX_CONTENT_LENGTH  = 16 * 1024 * 1024   # 16 MB max upload
    DEFAULT_PAGE_SIZE   = 10
    MAX_PAGE_SIZE       = 100


class DevelopmentConfig(Config):
    """Development — SQLite file in flask-backend/, full debug output."""
    DEBUG = True
    SQLALCHEMY_ECHO = False   # Flip to True to see SQL in console


class TestingConfig(Config):
    """Testing — in-memory SQLite, tables created fresh each test run."""
    DEBUG   = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production — expects DATABASE_URL env var (SQLite path or Postgres URI)."""
    DEBUG   = False
    TESTING = False
    JWT_COOKIE_SECURE      = True
    SESSION_COOKIE_SECURE  = True


# ── Config map ────────────────────────────────────────────────────────────────
config_map = {
    'development': DevelopmentConfig,
    'testing':     TestingConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}


def get_config(env=None):
    """Return the appropriate config class based on environment."""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)