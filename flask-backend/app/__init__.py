"""
Flask Application Factory
Creates and configures the Flask app instance
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from config import get_config
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(env=None):
    """
    Application factory function.
    Creates and returns a configured Flask application.
    """
    # Load environment variables
    load_dotenv()

    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    config = get_config(env)
    app.config.from_object(config)

    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Initialize JWT
    jwt = JWTManager(app)

    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({
            'success': False,
            'message': 'Authorization token is missing or invalid'
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token has expired. Please log in again.'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Token is invalid'
        }), 401

    # Initialize database (skip real connection in testing - use mongomock)
    if not app.config.get('TESTING'):
        init_db(app)
    else:
        # Set up a mock db for testing
        import mongomock
        mock_client = mongomock.MongoClient()
        app.db_client = mock_client
        app.db = mock_client[app.config.get('MONGO_DBNAME', 'website-builder-test')]
        # Also set the global db reference for the get_db() helper
        import app.database as db_module
        db_module._client = mock_client
        db_module._db = app.db

    # Register blueprints
    _register_blueprints(app)

    # Register global error handlers
    _register_error_handlers(app)

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'message': 'Website Builder API is running',
            'version': '2.0.0',
            'backend': 'Python Flask'
        }), 200

    logger.info(f"✅ Flask app created in '{app.config.get('FLASK_ENV', 'development')}' mode")
    return app


def _register_blueprints(app):
    """Register all application blueprints."""
    from app.blueprints.auth import auth_bp
    from app.blueprints.users import users_bp
    from app.blueprints.websites import websites_bp
    from app.blueprints.subscriptions import subscriptions_bp
    from app.blueprints.payments import payments_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.plugins import plugins_bp
    from app.blueprints.templates import templates_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(websites_bp, url_prefix='/api/websites')
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(plugins_bp, url_prefix='/api/plugins')
    app.register_blueprint(templates_bp, url_prefix='/api/templates')

    logger.info("✅ All blueprints registered successfully")


def _register_error_handlers(app):
    """Register global HTTP error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request',
            'error': str(error)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'message': 'Unauthorized - authentication required'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': 'Forbidden - insufficient permissions'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'message': 'Unprocessable entity - validation error'
        }), 422

    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            'success': False,
            'message': 'Too many requests - please slow down'
        }), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500