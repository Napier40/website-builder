"""
MongoDB Database Connection Manager
Uses PyMongo for direct MongoDB access
"""
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

# Global database client and db reference
_client = None
_db = None


def init_db(app):
    """
    Initialize MongoDB connection using the Flask app config.
    Stores client and db references as app extensions.
    """
    global _client, _db

    mongo_uri = app.config.get('MONGO_URI', 'mongodb://localhost:27017/website-builder')
    db_name = app.config.get('MONGO_DBNAME', 'website-builder')

    try:
        _client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=10000
        )
        # Verify the connection
        _client.admin.command('ping')
        _db = _client[db_name]

        # Store on app for access via current_app
        app.db_client = _client
        app.db = _db

        logger.info(f"✅ MongoDB connected successfully to database: {db_name}")
        _create_indexes(_db)
        return _db

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        # Don't raise in testing mode - mongomock will be used
        if not app.config.get('TESTING'):
            raise


def get_db():
    """
    Get the current database instance.
    Returns the global db reference.
    """
    global _db
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first.")
    return _db


def close_db(app=None):
    """Close the database connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed.")


def _create_indexes(db):
    """Create necessary MongoDB indexes for performance."""
    try:
        # Users collection indexes
        db.users.create_index('email', unique=True)
        db.users.create_index('role')
        db.users.create_index('subscriptionStatus')
        db.users.create_index('createdAt')

        # Websites collection indexes
        db.websites.create_index('subdomain', unique=True)
        db.websites.create_index('user')
        db.websites.create_index('isPublished')
        db.websites.create_index('moderationStatus')
        db.websites.create_index('createdAt')

        # Subscriptions collection indexes
        db.subscriptions.create_index('name', unique=True)

        # Payments collection indexes
        db.payments.create_index('user')
        db.payments.create_index('stripePaymentIntentId')
        db.payments.create_index('createdAt')

        # Audit logs collection indexes
        db.audit_logs.create_index('user')
        db.audit_logs.create_index('action')
        db.audit_logs.create_index('timestamp')
        db.audit_logs.create_index('resourceModel')

        # Moderation collection indexes
        db.moderation.create_index('status')
        db.moderation.create_index('contentModel')
        db.moderation.create_index('createdAt')

        # Templates collection indexes
        db.templates.create_index('category')
        db.templates.create_index('isPremium')
        db.templates.create_index('isPublic')

        # Plugins collection indexes
        db.plugins.create_index('name', unique=True)
        db.plugins.create_index('isActive')

        logger.info("✅ MongoDB indexes created successfully.")
    except Exception as e:
        logger.warning(f"⚠️  Index creation warning: {e}")