"""
Flask Application Factory
"""
import os
import logging
from flask import Flask, jsonify, Response, redirect, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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

    # Root route — friendly HTML landing page instead of raw JSON.
    # If someone hits the backend directly in a browser, redirect them to the
    # frontend (when configured) or show a helpful status page.
    @app.route('/', methods=['GET'])
    def index():
        # If the request explicitly asks for JSON (API client / curl with Accept header),
        # keep returning JSON for backwards compatibility.
        accept = request.headers.get('Accept', '')
        wants_json = 'application/json' in accept and 'text/html' not in accept

        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

        if wants_json:
            return jsonify({
                'success': True,
                'message': 'Website Builder API',
                'version': '3.0.0',
                'docs':    '/api/health',
                'hint':    'All endpoints are prefixed with /api/',
                'frontend_url': frontend_url,
            }), 200

        # Otherwise, serve a human-friendly HTML landing page
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Builder API — Backend is Running</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }}
        .container {{
            max-width: 720px;
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 3rem;
            backdrop-filter: blur(10px);
        }}
        .badge {{
            display: inline-block;
            background: rgba(0, 255, 136, 0.15);
            color: #00ff88;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(0, 255, 136, 0.3);
        }}
        h1 {{
            font-size: 2.25rem;
            margin-bottom: 0.75rem;
            background: linear-gradient(135deg, #00ff88, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        p.lead {{
            color: rgba(255, 255, 255, 0.75);
            margin-bottom: 2rem;
            font-size: 1.05rem;
            line-height: 1.6;
        }}
        .section {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
        }}
        .section h2 {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: rgba(255, 255, 255, 0.5);
            margin-bottom: 0.75rem;
        }}
        .section a, .section code {{
            color: #00d4ff;
            text-decoration: none;
            font-family: 'SF Mono', Monaco, Consolas, monospace;
            font-size: 0.95rem;
        }}
        .section a:hover {{ text-decoration: underline; }}
        .cta {{
            display: inline-block;
            margin-top: 1rem;
            background: linear-gradient(135deg, #00ff88, #00d4ff);
            color: #0a0a0a;
            padding: 0.85rem 1.75rem;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            transition: transform 0.2s;
        }}
        .cta:hover {{ transform: translateY(-2px); }}
        .status-dot {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ff88;
            margin-right: 0.5rem;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
        }}
        .muted {{ color: rgba(255, 255, 255, 0.5); font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <span class="badge"><span class="status-dot"></span>API Online</span>
        <h1>Website Builder API</h1>
        <p class="lead">
            You've reached the <strong>backend API server</strong> (Flask + SQLite).
            This service powers the Website Builder application — it does not serve
            the user interface directly.
        </p>

        <div class="section">
            <h2>👉 Go to the App</h2>
            <p class="muted" style="margin-bottom: 0.75rem;">
                The user interface runs separately on the React frontend:
            </p>
            <a class="cta" href="{frontend_url}">Open Website Builder →</a>
        </div>

        <div class="section">
            <h2>API Endpoints</h2>
            <p>All endpoints are prefixed with <code>/api/</code></p>
            <p style="margin-top: 0.5rem;">
                Health check: <a href="/api/health">/api/health</a>
            </p>
        </div>

        <div class="section">
            <h2>Available Routes</h2>
            <p><code>/api/auth/*</code> &nbsp;·&nbsp; <code>/api/users/*</code> &nbsp;·&nbsp; <code>/api/websites/*</code></p>
            <p style="margin-top: 0.4rem;"><code>/api/subscriptions/*</code> &nbsp;·&nbsp; <code>/api/payments/*</code> &nbsp;·&nbsp; <code>/api/admin/*</code></p>
        </div>

        <p class="muted" style="margin-top: 2rem; text-align: center;">
            Website Builder v3.0.0 · Flask + SQLite + React
        </p>
    </div>
</body>
</html>"""
        return Response(html, mimetype='text/html'), 200

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
    from app.blueprints.catalogue     import catalogue_bp
    from app.blueprints.render        import preview_bp, public_bp
    from app.blueprints.translations import translations_bp

    app.register_blueprint(auth_bp,          url_prefix='/api/auth')
    app.register_blueprint(users_bp,         url_prefix='/api/users')
    app.register_blueprint(websites_bp,      url_prefix='/api/websites')
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')
    app.register_blueprint(payments_bp,      url_prefix='/api/payments')
    app.register_blueprint(admin_bp,         url_prefix='/api/admin')
    app.register_blueprint(plugins_bp,       url_prefix='/api/plugins')
    app.register_blueprint(templates_bp,     url_prefix='/api/templates')
    app.register_blueprint(catalogue_bp,     url_prefix='/api/catalogue')
    app.register_blueprint(translations_bp,  url_prefix='/api/i18n')
    # Editor preview shares the /api/websites namespace so URLs are predictable.
    app.register_blueprint(preview_bp,       url_prefix='/api/websites')
    # Public published-site serving lives at the root ("/s/<subdomain>").
    app.register_blueprint(public_bp)

    logger.info("✅ All blueprints registered")


def _register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'success': False, 'message': 'Bad request', 'error': str(e)}), 400

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({
            'success': False,
            'message': 'Rate limit exceeded. Please slow down.',
            'error': 'too_many_requests'
        }), 429

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