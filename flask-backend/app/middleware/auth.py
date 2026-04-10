"""
Authentication & Authorization Middleware
Flask decorators for JWT protection, role-based access, and subscription checks
"""
import logging
from functools import wraps
from flask import jsonify, request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import UserModel

logger = logging.getLogger(__name__)


def jwt_required_custom(fn):
    """
    Decorator: validates JWT token and loads the current user into flask.g.
    Replaces the need to call verify_jwt_in_request() manually in every route.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = UserModel.find_by_id(user_id)

            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found - token may be stale'
                }), 401

            if not user.get('isActive', True):
                return jsonify({
                    'success': False,
                    'message': 'Account is deactivated. Please contact support.'
                }), 403

            # Store user in flask.g for access in route handlers
            g.current_user = user
            g.user_id = str(user['_id'])

        except Exception as e:
            logger.warning(f"JWT verification failed: {e}")
            return jsonify({
                'success': False,
                'message': 'Not authorized to access this route'
            }), 401

        return fn(*args, **kwargs)
    return wrapper


def authorize(*roles):
    """
    Decorator factory: restricts a route to users with specific roles.
    Must be used AFTER @jwt_required_custom.

    Usage:
        @jwt_required_custom
        @authorize('admin')
        def admin_only_route():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if not user or user.get('role') not in roles:
                return jsonify({
                    'success': False,
                    'message': f"Access denied. Required role(s): {', '.join(roles)}"
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def check_subscription(*subscription_types):
    """
    Decorator factory: restricts a route to users with specific subscription levels.
    Must be used AFTER @jwt_required_custom.

    Usage:
        @jwt_required_custom
        @check_subscription('premium', 'enterprise')
        def premium_feature():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Authentication required'
                }), 401

            # Admins bypass subscription checks
            if user.get('role') == 'admin':
                return fn(*args, **kwargs)

            if user.get('subscriptionStatus') not in subscription_types:
                return jsonify({
                    'success': False,
                    'message': (
                        f"This feature requires one of the following subscription plans: "
                        f"{', '.join(subscription_types)}. "
                        f"Please upgrade your subscription."
                    )
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def audit_log_request(action: str, resource_model: str = None):
    """
    Decorator factory: automatically creates an audit log entry after a request.
    Non-blocking - failures are silently swallowed.

    Usage:
        @jwt_required_custom
        @audit_log_request('CREATE', 'Website')
        def create_website():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            response = fn(*args, **kwargs)

            try:
                from app.models.audit_log import AuditLogModel
                user = getattr(g, 'current_user', None)
                if user:
                    AuditLogModel.create_log(
                        user_id=str(user['_id']),
                        action=action,
                        resource=request.path,
                        resource_model=resource_model,
                        details={
                            'method': request.method,
                            'endpoint': request.endpoint
                        },
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', '')
                    )
            except Exception as e:
                logger.warning(f"Audit log decorator failed (non-critical): {e}")

            return response
        return wrapper
    return decorator