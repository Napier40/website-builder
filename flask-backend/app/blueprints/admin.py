"""
Admin Blueprint — dashboard, user management, moderation, audit logs
"""
from flask import Blueprint, request, g

from app.models.user       import User
from app.models.website    import Website
from app.models.payment    import Payment
from app.models.audit_log  import AuditLog
from app.models.moderation import Moderation
from app.middleware.auth   import jwt_required_custom, authorize
from app.utils.helpers     import (success_response, error_response,
                                    paginated_response, get_pagination_params)

admin_bp = Blueprint('admin', __name__)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def dashboard():
    from app.database import db
    total_users    = User.count()
    total_websites = Website.query.count()
    total_payments = Payment.query.count()
    pending_mod    = Moderation.query.filter_by(status='pending').count()

    return success_response(data={
        'stats': {
            'totalUsers':           total_users,
            'totalAdmins':          User.count(role='admin'),
            'totalWebsites':        total_websites,
            'publishedWebsites':    Website.query.filter_by(is_published=True).count(),
            'pendingModeration':    pending_mod,
            'totalPayments':        total_payments,
        }
    })


# ── User management ───────────────────────────────────────────────────────────

@admin_bp.route('/users', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_users():
    page, limit, _ = get_pagination_params()
    search = request.args.get('search')
    role   = request.args.get('role')
    users, total = User.find_all(search=search, role=role, page=page, limit=limit)
    return paginated_response([u.to_dict() for u in users], total, page, limit)


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_user(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return error_response('User not found', 404)
    return success_response(data={'user': user.to_dict()})


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_user(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return error_response('User not found', 404)

    data    = request.get_json(silent=True) or {}
    allowed = {k: v for k, v in data.items()
               if k in ('name', 'role', 'subscription_type', 'subscription_status')}
    user.update(**allowed)

    AuditLog.create_log(user_id=g.current_user.id, action='ADMIN_ACTION',
                        resource_model='User', resource_id=user_id,
                        description=f'Admin updated user {user_id}')
    return success_response(data={'user': user.to_dict()}, message='User updated')


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
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


# ── Moderation ────────────────────────────────────────────────────────────────

@admin_bp.route('/moderation', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_moderation_queue():
    page, limit, _ = get_pagination_params()
    status         = request.args.get('status', 'pending')
    items, total   = Moderation.find_all(page=page, limit=limit, status=status)
    return paginated_response([m.to_dict() for m in items], total, page, limit)


@admin_bp.route('/moderation', methods=['POST'])
@jwt_required_custom
def create_moderation_report():
    """Any authenticated user can report content."""
    data = request.get_json(silent=True) or {}
    missing = [f for f in ('contentId', 'contentModel', 'reason') if not data.get(f)]
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    mod = Moderation.create(
        content_id=data['contentId'],
        content_model=data['contentModel'],
        reporter_id=g.current_user.id,
        reason=data['reason'],
        original_content=data.get('originalContent'),
    )
    return success_response(data={'moderation': mod.to_dict()},
                            message='Report submitted', status_code=201)


@admin_bp.route('/moderation/<int:mod_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def review_moderation(mod_id):
    mod = Moderation.find_by_id(mod_id)
    if not mod:
        return error_response('Moderation record not found', 404)

    data   = request.get_json(silent=True) or {}
    status = data.get('status')
    if status not in ('approved', 'rejected', 'pending'):
        return error_response('Status must be approved, rejected, or pending', 400)

    mod.review(admin_id=g.current_user.id, status=status,
               notes=data.get('notes', ''))

    AuditLog.create_log(user_id=g.current_user.id, action='MODERATION',
                        resource_model='Moderation', resource_id=mod_id,
                        description=f'Moderation {mod_id} set to {status}')
    return success_response(data={'moderation': mod.to_dict()},
                            message=f'Moderation record {status}')


# ── Website content override ──────────────────────────────────────────────────

@admin_bp.route('/websites/<int:website_id>/override', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def override_website(website_id):
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    data = request.get_json(silent=True) or {}
    website.admin_override(admin_id=g.current_user.id,
                           reason=data.get('reason', ''))

    AuditLog.create_log(user_id=g.current_user.id, action='CONTENT_OVERRIDE',
                        resource_model='Website', resource_id=website_id,
                        description=data.get('reason', 'Admin override'))
    return success_response(data={'website': website.to_dict()},
                            message='Website override applied')


@admin_bp.route('/websites/<int:website_id>/delete-content', methods=['DELETE'])
@jwt_required_custom
@authorize('admin')
def delete_website_content(website_id):
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    # Remove all pages
    from app.models.website import Page
    from app.database import db
    Page.query.filter_by(website_id=website_id).delete()
    db.session.commit()

    AuditLog.create_log(user_id=g.current_user.id, action='DELETE',
                        resource_model='Website', resource_id=website_id,
                        description='Admin deleted all pages from website')
    return success_response(message='Website content deleted')


# ── Audit logs ────────────────────────────────────────────────────────────────

@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_audit_logs():
    page, limit, _ = get_pagination_params(default_limit=50)
    action         = request.args.get('action')
    user_id        = request.args.get('userId', type=int)
    items, total   = AuditLog.find_all(page=page, limit=limit,
                                       action=action, user_id=user_id)
    return paginated_response([log.to_dict() for log in items], total, page, limit)