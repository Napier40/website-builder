"""
Flask Application Configuration
Supports Development, Testing, and Production environments
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared across all environments."""
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 2592000)))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/website-builder')
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'website-builder')

    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

    CORS_ORIGINS = [os.environ.get('FRONTEND_URL', 'http://localhost:3000')]

    DEBUG = False
    TESTING = False

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')

    # Pagination defaults
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration - uses an isolated test database."""
    DEBUG = True
    TESTING = True
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/website-builder-test')
    MONGO_DBNAME = 'website-builder-test'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration with strict security settings."""
    DEBUG = False
    TESTING = False
    # In production, ensure environment variables are set properly
    JWT_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True


# Configuration map
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Return the appropriate config class based on environment."""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)