"""
Users Blueprint — admin user management
"""
from flask import Blueprint, request, g

from app.models.user      import User
from app.models.audit_log import AuditLog
from app.middleware.auth  import jwt_required_custom, authorize
from app.utils.helpers    import (success_response, error_response,
                                   paginated_response, get_pagination_params)

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_all_users():
    page, limit, _ = get_pagination_params()
    search = request.args.get('search')
    role   = request.args.get('role')

    users, total = User.find_all(search=search, role=role, page=page, limit=limit)
    return paginated_response([u.to_dict() for u in users], total, page, limit)


@users_bp.route('/stats', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_user_stats():
    return success_response(data={
        'total':      User.count(),
        'admins':     User.count(role='admin'),
        'users':      User.count(role='user'),
    })


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_user(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return error_response('User not found', 404)
    return success_response(data={'user': user.to_dict()})


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_user(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return error_response('User not found', 404)

    data    = request.get_json(silent=True) or {}
    allowed = {k: v for k, v in data.items()
               if k in ('name', 'role', 'subscription_type', 'subscription_status')}
    if not allowed:
        return error_response('No valid fields to update', 400)

    user.update(**allowed)
    AuditLog.create_log(user_id=g.current_user.id, action='ADMIN_ACTION',
                        resource_model='User', resource_id=user_id,
                        description=f'Admin updated user {user_id}')
    return success_response(data={'user': user.to_dict()}, message='User updated')


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required_custom
@authorize('admin')
def delete_user(user_id):
    if user_id == g.current_user.id:
        return error_response('Cannot delete your own account', 400)

    user = User.find_by_id(user_id)
    if not user:
        return error_response('User not found', 404)

    user.delete()
    AuditLog.create_log(user_id=g.current_user.id, action='DELETE',
                        resource_model='User', resource_id=user_id,
                        description=f'Admin deleted user {user_id}')
    return success_response(message='User deleted')