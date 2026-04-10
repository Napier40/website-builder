"""
Admin Blueprint
Routes: /api/admin - dashboard, user management, moderation, audit logs, content override
"""
import logging
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, g

from app.models.user import UserModel
from app.models.website import WebsiteModel
from app.models.payment import PaymentModel
from app.models.audit_log import AuditLogModel
from app.models.moderation import ModerationModel
from app.middleware.auth import jwt_required_custom, authorize
from app.utils.helpers import (
    error_response, paginated_response, get_pagination_params,
    get_sort_params, validate_object_id
)

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)


# ─── Dashboard ────────────────────────────────────────────────────────────────

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_dashboard_stats():
    """
    Get comprehensive admin dashboard statistics.
    GET /api/admin/dashboard
    """
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    total_users = UserModel.count()
    new_users = UserModel.count({'createdAt': {'$gte': thirty_days_ago}})
    subscription_stats = UserModel.aggregate_subscription_stats()

    total_websites = WebsiteModel.count()
    published_websites = WebsiteModel.count({'isPublished': True})

    monthly_revenue = PaymentModel.aggregate_monthly_revenue(days=30)

    moderation_stats = ModerationModel.aggregate_stats()

    return jsonify({
        'success': True,
        'data': {
            'users': {
                'total': total_users,
                'new30Days': new_users,
                'subscriptions': subscription_stats
            },
            'websites': {
                'total': total_websites,
                'published': published_websites
            },
            'revenue': {
                'monthly': monthly_revenue
            },
            'moderation': moderation_stats
        }
    }), 200


# ─── User Management ──────────────────────────────────────────────────────────

@admin_bp.route('/users', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_users():
    """
    Get all users with filtering and pagination.
    GET /api/admin/users
    Query: search, role, subscriptionStatus, page, limit, sort
    """
    page, limit, skip = get_pagination_params()
    sort_field, sort_dir = get_sort_params('createdAt')
    query = {}

    search = request.args.get('search', '').strip()
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'email': {'$regex': search, '$options': 'i'}}
        ]

    for filter_field in ('role', 'subscriptionStatus'):
        val = request.args.get(filter_field, '').strip()
        if val:
            query[filter_field] = val

    users, total = UserModel.find_all(query, skip, limit, sort_field, sort_dir)
    return paginated_response(users, total, page, limit)


@admin_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_user(user_id):
    """Get a specific user with context. GET /api/admin/users/<user_id>"""
    if not validate_object_id(user_id):
        return error_response('Invalid user ID format', 400)

    user = UserModel.find_by_id(user_id)
    if not user:
        return error_response(f'User not found: {user_id}', 404)

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


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_user(user_id):
    """Update any user field as admin. PUT /api/admin/users/<user_id>"""
    if not validate_object_id(user_id):
        return error_response('Invalid user ID format', 400)

    user = UserModel.find_by_id(user_id)
    if not user:
        return error_response(f'User not found: {user_id}', 404)

    data = request.get_json() or {}
    original = {k: user.get(k) for k in ('name', 'email', 'role', 'subscriptionStatus', 'isActive')}

    allowed = ['name', 'email', 'role', 'subscriptionStatus', 'isActive']
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return error_response('No valid fields to update', 400)

    updated_user = UserModel.update_by_id(user_id, updates)

    AuditLogModel.create_log(
        user_id=g.user_id, action='ADMIN_ACTION',
        resource=f'/api/admin/users/{user_id}',
        resource_id=user_id, resource_model='User',
        previous_state=original, new_state=updates,
        details={'action': 'ADMIN_UPDATE_USER'}
    )

    return jsonify({'success': True, 'data': updated_user}), 200


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required_custom
@authorize('admin')
def delete_user(user_id):
    """Delete a user account. DELETE /api/admin/users/<user_id>"""
    if not validate_object_id(user_id):
        return error_response('Invalid user ID format', 400)

    if user_id == g.user_id:
        return error_response('You cannot delete your own account', 400)

    user = UserModel.find_by_id(user_id)
    if not user:
        return error_response(f'User not found: {user_id}', 404)

    AuditLogModel.create_log(
        user_id=g.user_id, action='ADMIN_ACTION',
        resource=f'/api/admin/users/{user_id}',
        resource_id=user_id, resource_model='User',
        previous_state=user,
        details={'action': 'ADMIN_DELETE_USER', 'email': user.get('email')}
    )

    UserModel.delete_by_id(user_id)
    return jsonify({'success': True, 'message': 'User deleted successfully', 'data': {}}), 200


# ─── Moderation Queue ─────────────────────────────────────────────────────────

@admin_bp.route('/moderation', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_moderation_queue():
    """
    Get the content moderation queue.
    GET /api/admin/moderation
    Query: status, contentModel, page, limit
    """
    page, limit, skip = get_pagination_params()
    query = {}

    status = request.args.get('status', 'pending').strip()
    if status:
        query['status'] = status

    content_model = request.args.get('contentModel', '').strip()
    if content_model:
        query['contentModel'] = content_model

    items, total = ModerationModel.find_all(query, skip, limit)
    return paginated_response(items, total, page, limit)


@admin_bp.route('/moderation', methods=['POST'])
@jwt_required_custom
@authorize('admin')
def flag_content():
    """
    Flag content for moderation.
    POST /api/admin/moderation
    Body: { contentId, contentModel, reason }
    """
    data = request.get_json() or {}
    content_id = data.get('contentId')
    content_model = data.get('contentModel')
    reason = data.get('reason', '')

    if not content_id or not content_model:
        return error_response('contentId and contentModel are required', 400)

    mod = ModerationModel.create(
        content_id=content_id,
        content_model=content_model,
        reporter_id=g.user_id,
        reason=reason
    )

    return jsonify({'success': True, 'data': mod}), 201


@admin_bp.route('/moderation/<mod_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def process_moderation(mod_id):
    """
    Process a moderation item (approve/reject with optional content changes).
    PUT /api/admin/moderation/<mod_id>
    Body: { status, reason, action, modifiedContent? }
    """
    if not validate_object_id(mod_id):
        return error_response('Invalid moderation ID format', 400)

    mod = ModerationModel.find_by_id(mod_id)
    if not mod:
        return error_response('Moderation item not found', 404)

    data = request.get_json() or {}
    status = data.get('status')
    reason = data.get('reason', '')
    action = data.get('action', 'no_action')
    modified_content = data.get('modifiedContent')

    updates = {
        'status': status,
        'reason': reason,
        'action': action,
        'moderator': g.user_id
    }
    if modified_content:
        updates['modifiedContent'] = modified_content

    updated_mod = ModerationModel.update_by_id(mod_id, updates)

    # If rejected website, apply moderation status
    if status in ('approved', 'rejected') and mod.get('contentModel') == 'Website':
        content_id = mod.get('content')
        if content_id:
            website_updates = {'moderationStatus': status}
            if status == 'rejected':
                website_updates['moderationReason'] = reason
                website_updates['isPublished'] = False
                if modified_content:
                    website_updates.update(modified_content)
            WebsiteModel.update_by_id(content_id, website_updates)

    AuditLogModel.create_log(
        user_id=g.user_id, action='MODERATION',
        resource=f'/api/admin/moderation/{mod_id}',
        resource_id=mod_id, resource_model='Moderation',
        details={'status': status, 'reason': reason, 'action': action}
    )

    return jsonify({'success': True, 'data': updated_mod}), 200


# ─── Content Override ─────────────────────────────────────────────────────────

@admin_bp.route('/websites/<website_id>/override', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def override_website_content(website_id):
    """
    Admin: override a website's page content.
    PUT /api/admin/websites/<website_id>/override
    Body: { content (pages array), reason }
    """
    if not validate_object_id(website_id):
        return error_response('Invalid website ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    data = request.get_json() or {}
    new_pages = data.get('content')
    reason = data.get('reason', 'Admin content override')

    if new_pages is None:
        return error_response('content (pages array) is required', 400)

    original_pages = website.get('pages', [])

    updated_website = WebsiteModel.admin_override(
        website_id=website_id,
        admin_id=g.user_id,
        new_pages=new_pages,
        reason=reason
    )

    # Create moderation record
    ModerationModel.create(
        content_id=website_id,
        content_model='Website',
        reporter_id=g.user_id,
        reason=reason,
        original_content={'pages': original_pages}
    )
    # Mark it as approved immediately (admin did the override)
    from app.database import get_db
    db = get_db()
    db.moderation.update_one(
        {'content': website_id},
        {'$set': {'status': 'approved', 'moderator': g.user_id, 'action': 'content_edited'}}
    )

    AuditLogModel.create_log(
        user_id=g.user_id, action='CONTENT_OVERRIDE',
        resource=f'/api/admin/websites/{website_id}/override',
        resource_id=website_id, resource_model='Website',
        previous_state={'pages': original_pages},
        new_state={'pages': new_pages},
        details={'reason': reason, 'websiteName': website.get('name')}
    )

    return jsonify({
        'success': True,
        'message': 'Website content overridden successfully',
        'data': updated_website
    }), 200


@admin_bp.route('/websites/<website_id>/delete-content', methods=['DELETE'])
@jwt_required_custom
@authorize('admin')
def delete_website_content(website_id):
    """
    Admin: delete inappropriate content / entire website.
    DELETE /api/admin/websites/<website_id>/delete-content
    Body: { reason }
    """
    if not validate_object_id(website_id):
        return error_response('Invalid website ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    data = request.get_json() or {}
    reason = data.get('reason', 'Admin removed inappropriate content')

    AuditLogModel.create_log(
        user_id=g.user_id, action='ADMIN_ACTION',
        resource=f'/api/admin/websites/{website_id}/delete-content',
        resource_id=website_id, resource_model='Website',
        previous_state={'name': website.get('name'), 'subdomain': website.get('subdomain')},
        details={'action': 'ADMIN_DELETE_WEBSITE', 'reason': reason}
    )

    WebsiteModel.delete_by_id(website_id)

    return jsonify({
        'success': True,
        'message': 'Website deleted by admin',
        'reason': reason
    }), 200


# ─── Audit Logs ───────────────────────────────────────────────────────────────

@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_audit_logs():
    """
    Get audit logs with filtering.
    GET /api/admin/audit-logs
    Query: user, action, resource, startDate, endDate, page, limit
    """
    page, limit, skip = get_pagination_params(default_limit=20)
    query = {}

    user_filter = request.args.get('user', '').strip()
    if user_filter and validate_object_id(user_filter):
        from bson import ObjectId
        query['user'] = ObjectId(user_filter)

    action = request.args.get('action', '').strip()
    if action:
        query['action'] = action

    resource = request.args.get('resource', '').strip()
    if resource:
        query['resource'] = {'$regex': resource, '$options': 'i'}

    start_date = request.args.get('startDate', '').strip()
    end_date = request.args.get('endDate', '').strip()
    if start_date or end_date:
        query['timestamp'] = {}
        if start_date:
            query['timestamp']['$gte'] = datetime.fromisoformat(start_date)
        if end_date:
            query['timestamp']['$lte'] = datetime.fromisoformat(end_date)

    logs, total = AuditLogModel.find_all(query, skip, limit)
    return paginated_response(logs, total, page, limit)