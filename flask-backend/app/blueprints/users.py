"""
Users Blueprint
Routes: /api/users (admin-only user management)
"""
import logging
from flask import Blueprint, request, jsonify, g

from app.models.user import UserModel
from app.models.website import WebsiteModel
from app.models.payment import PaymentModel
from app.models.audit_log import AuditLogModel
from app.middleware.auth import jwt_required_custom, authorize
from app.utils.helpers import (
    validate_email, validate_object_id,
    error_response, success_response, paginated_response,
    get_pagination_params, get_sort_params
)

logger = logging.getLogger(__name__)
users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_all_users():
    """
    Get all users with search, filter, and pagination.
    GET /api/users
    Query: search, role, subscriptionStatus, page, limit, sort
    """
    page, limit, skip = get_pagination_params()
    sort_field, sort_dir = get_sort_params('createdAt')

    query = {}

    # Search by name or email
    search = request.args.get('search', '').strip()
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'email': {'$regex': search, '$options': 'i'}}
        ]

    role = request.args.get('role', '').strip()
    if role:
        query['role'] = role

    sub_status = request.args.get('subscriptionStatus', '').strip()
    if sub_status:
        query['subscriptionStatus'] = sub_status

    users, total = UserModel.find_all(query, skip, limit, sort_field, sort_dir)
    return paginated_response(users, total, page, limit)


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_user_by_id(user_id):
    """
    Get a specific user with their websites, payments, and audit logs.
    GET /api/users/<user_id>
    """
    if not validate_object_id(user_id):
        return error_response('Invalid user ID format', 400)

    user = UserModel.find_by_id(user_id)
    if not user:
        return error_response(f'User not found with id {user_id}', 404)

    websites = WebsiteModel.find_by_user(user_id)
    payments, _ = PaymentModel.find_by_user(user_id, limit=5)
    audit_logs = AuditLogModel.find_by_user(user_id, limit=10)

    return jsonify({
        'success': True,
        'data': {
            'user': user,
            'websites': {'count': len(websites), 'items': websites},
            'payments': {'count': len(payments), 'items': payments},
            'auditLogs': {'count': len(audit_logs), 'items': audit_logs}
        }
    }), 200


@users_bp.route('/<user_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_user(user_id):
    """
    Admin update a user (role, subscriptionStatus, isActive, name, email).
    PUT /api/users/<user_id>
    """
    if not validate_object_id(user_id):
        return error_response('Invalid user ID format', 400)

    data = request.get_json()
    if not data:
        return error_response('Request body must be JSON', 400)

    user = UserModel.find_by_id(user_id)
    if not user:
        return error_response(f'User not found with id {user_id}', 404)

    # Capture original state for audit log
    original_state = {k: user.get(k) for k in ('name', 'email', 'role', 'subscriptionStatus', 'isActive')}

    updates = {}
    allowed = ['name', 'email', 'role', 'subscriptionStatus', 'isActive']
    for field in allowed:
        if field in data:
            updates[field] = data[field]

    if 'email' in updates and not validate_email(updates['email']):
        return error_response('Please provide a valid email address', 400)

    if not updates:
        return error_response('No valid fields to update', 400)

    updated_user = UserModel.update_by_id(user_id, updates)

    # Audit log
    AuditLogModel.create_log(
        user_id=g.user_id,
        action='ADMIN_ACTION',
        resource=f'/api/users/{user_id}',
        resource_id=user_id,
        resource_model='User',
        previous_state=original_state,
        new_state=updates,
        details={'action': 'UPDATE_USER', 'updatedFields': list(updates.keys())}
    )

    return jsonify({
        'success': True,
        'message': 'User updated successfully',
        'data': updated_user
    }), 200


@users_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required_custom
@authorize('admin')
def delete_user(user_id):
    """
    Delete a user account.
    DELETE /api/users/<user_id>
    """
    if not validate_object_id(user_id):
        return error_response('Invalid user ID format', 400)

    user = UserModel.find_by_id(user_id)
    if not user:
        return error_response(f'User not found with id {user_id}', 404)

    # Prevent admins from deleting themselves
    if user_id == g.user_id:
        return error_response('You cannot delete your own account', 400)

    # Audit log before deletion
    AuditLogModel.create_log(
        user_id=g.user_id,
        action='ADMIN_ACTION',
        resource=f'/api/users/{user_id}',
        resource_id=user_id,
        resource_model='User',
        previous_state=user,
        details={'action': 'DELETE_USER', 'deletedUserEmail': user.get('email')}
    )

    deleted = UserModel.delete_by_id(user_id)
    if not deleted:
        return error_response('Failed to delete user', 500)

    return jsonify({
        'success': True,
        'message': 'User deleted successfully',
        'data': {}
    }), 200


@users_bp.route('/stats', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_user_stats():
    """
    Get user statistics for the admin dashboard.
    GET /api/users/stats
    """
    from datetime import datetime, timezone, timedelta

    total = UserModel.count()
    new_30d = UserModel.count({
        'createdAt': {'$gte': datetime.now(timezone.utc) - timedelta(days=30)}
    })
    subscription_stats = UserModel.aggregate_subscription_stats()

    return jsonify({
        'success': True,
        'data': {
            'total': total,
            'new30Days': new_30d,
            'bySubscription': subscription_stats
        }
    }), 200