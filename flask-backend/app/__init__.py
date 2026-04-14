"""
Flask Application Factory
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from config import get_config
from app.database import db, init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(env=None):
    """
    Application factory. Creates and returns a configured Flask app.
    Uses SQLite — no separate database installation required.
    """
    load_dotenv()

    app = Flask(__name__)

    # Load config
    config = get_config(env)
    app.config.from_object(config)

    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins":      app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
            "methods":      ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers":["Content-Type", "Authorization"],
        }
    })

    # JWT
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({'success': False, 'message': 'Authorization token is missing or invalid'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'success': False, 'message': 'Token has expired. Please log in again.'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'success': False, 'message': 'Token is invalid'}), 401

    # Database — SQLite, created automatically
    init_db(app)

    # Blueprints
    _register_blueprints(app)

    # Error handlers
    _register_error_handlers(app)

    # Root route — helpful message instead of 404
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'success': True,
            'message': 'Website Builder API',
            'version': '3.0.0',
            'docs':    '/api/health',
            'hint':    'All endpoints are prefixed with /api/',
        }), 200

    # Health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'status':  'ok',
            'message': 'Website Builder API is running',
            'version': '2.0.0',
            'backend': 'Python Flask',
            'database': {
                'status':  'connected',
                'engine':  'SQLite',
                'message': 'SQLite database is ready',
            }
        }), 200

    logger.info(f"✅ Flask app created in '{app.config.get('FLASK_ENV', 'development')}' mode")
    return app


def _register_blueprints(app):
    from app.blueprints.auth          import auth_bp
    from app.blueprints.users         import users_bp
    from app.blueprints.websites      import websites_bp
    from app.blueprints.subscriptions import subscriptions_bp
    from app.blueprints.payments      import payments_bp
    from app.blueprints.admin         import admin_bp
    from app.blueprints.plugins       import plugins_bp
    from app.blueprints.templates     import templates_bp

    app.register_blueprint(auth_bp,          url_prefix='/api/auth')
    app.register_blueprint(users_bp,         url_prefix='/api/users')
    app.register_blueprint(websites_bp,      url_prefix='/api/websites')
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')
    app.register_blueprint(payments_bp,      url_prefix='/api/payments')
    app.register_blueprint(admin_bp,         url_prefix='/api/admin')
    app.register_blueprint(plugins_bp,       url_prefix='/api/plugins')
    app.register_blueprint(templates_bp,     url_prefix='/api/templates')

    logger.info("✅ All blueprints registered")


def _register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'success': False, 'message': 'Bad request', 'error': str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'success': False, 'message': 'Forbidden — insufficient permissions'}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'message': 'Resource not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'success': False, 'message': 'Method not allowed'}), 405

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({'success': False, 'message': 'Unprocessable entity'}), 422

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500