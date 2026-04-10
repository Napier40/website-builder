"""
Authentication & Authorisation Middleware
Decorators for JWT verification, role-based access control,
subscription gating, and audit logging.
"""
import logging
from functools import wraps
from flask import g, jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

logger = logging.getLogger(__name__)


# ── JWT verification ──────────────────────────────────────────────────────────

def jwt_required_custom(f):
    """
    Verify the JWT Bearer token and load the current user into flask.g.
    Must be applied before @authorize or @check_subscription.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()

            from app.models.user import User
            user = User.find_by_id(user_id)
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 401

            g.current_user = user
            return f(*args, **kwargs)

        except Exception as e:
            logger.debug(f"JWT verification failed: {e}")
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

    return decorated


# ── Role-based access control ─────────────────────────────────────────────────

def authorize(*roles):
    """
    Restrict access to users with one of the given roles.
    Must be used after @jwt_required_custom.

    Usage:
        @jwt_required_custom
        @authorize('admin')
        def admin_only_route(): ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if not user:
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            if roles and user.role not in roles:
                return jsonify({
                    'success': False,
                    'message': f"Access denied — required role: {' or '.join(roles)}"
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── Subscription gating ───────────────────────────────────────────────────────

def check_subscription(*subscription_types):
    """
    Restrict access to users on specific subscription plans.
    Must be used after @jwt_required_custom.

    Usage:
        @jwt_required_custom
        @check_subscription('premium', 'enterprise')
        def premium_route(): ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if not user:
                return jsonify({'success': False, 'message': 'Authentication required'}), 401

            # Admins bypass subscription checks
            if user.role == 'admin':
                return f(*args, **kwargs)

            if subscription_types and user.subscription_type not in subscription_types:
                return jsonify({
                    'success': False,
                    'message': f"This feature requires a {' or '.join(subscription_types)} subscription",
                    'upgradeRequired': True,
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── Audit logging decorator ───────────────────────────────────────────────────

def audit_log_request(action, resource_model=None):
    """
    Automatically create an audit log entry after a successful request.
    Must be used after @jwt_required_custom.

    Usage:
        @jwt_required_custom
        @audit_log_request('CREATE', 'Website')
        def create_website(): ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            response = f(*args, **kwargs)

            # Only log on success (2xx responses)
            try:
                status_code = response[1] if isinstance(response, tuple) else 200
                if 200 <= status_code < 300:
                    user = getattr(g, 'current_user', None)
                    from app.models.audit_log import AuditLog
                    AuditLog.create_log(
                        user_id=user.id if user else None,
                        action=action,
                        resource_model=resource_model,
                        ip_address=_get_client_ip(),
                        user_agent=request.headers.get('User-Agent', '')[:255],
                    )
            except Exception as e:
                logger.warning(f"Audit log decorator failed (non-fatal): {e}")

            return response
        return decorated
    return decorator


def _get_client_ip():
    forwarded = request.environ.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'