"""
Websites Blueprint
"""
from flask import Blueprint, request, g

from app.models.website   import Website
from app.models.user      import User
from app.models.audit_log import AuditLog
from app.middleware.auth  import jwt_required_custom, authorize
from app.utils.helpers    import (success_response, error_response,
                                   paginated_response, get_pagination_params,
                                   validate_required_fields, validate_subdomain)

websites_bp = Blueprint('websites', __name__)

# Subscription limits
WEBSITE_LIMITS = {'free': 1, 'premium': 5, 'enterprise': 999}
PAGE_LIMITS    = {'free': 5, 'premium': 50, 'enterprise': 999}


def _check_website_limit(user):
    """Return error response if user has reached their website limit, else None."""
    if user.role == 'admin':
        return None
    limit   = WEBSITE_LIMITS.get(user.subscription_type, 1)
    current = Website.count_by_user(user.id)
    if current >= limit:
        return error_response(
            f'Website limit reached ({limit}) for your {user.subscription_type} plan. '
            'Upgrade to create more websites.', 403)
    return None


# ── User routes ───────────────────────────────────────────────────────────────

@websites_bp.route('/', methods=['GET'])
@jwt_required_custom
def get_my_websites():
    page, limit, _ = get_pagination_params()
    items, total   = Website.find_by_user(g.current_user.id, page=page, limit=limit)
    return paginated_response([w.to_dict() for w in items], total, page, limit)


@websites_bp.route('/', methods=['POST'])
@jwt_required_custom
def create_website():
    limit_err = _check_website_limit(g.current_user)
    if limit_err:
        return limit_err

    data    = request.get_json(silent=True)
    if not data:
        return error_response('Request body must be JSON', 400)

    missing = validate_required_fields(data, ['name', 'subdomain'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    if not validate_subdomain(data['subdomain']):
        return error_response(
            'Invalid subdomain. Use 3-63 lowercase letters, digits, or hyphens.', 400)

    try:
        website = Website.create(
            name=data['name'],
            subdomain=data['subdomain'],
            user_id=g.current_user.id,
            template=data.get('template', 'blank'),
        )
    except ValueError as e:
        return error_response(str(e), 409)

    AuditLog.create_log(user_id=g.current_user.id, action='CREATE',
                        resource_model='Website', resource_id=website.id)
    return success_response(data={'website': website.to_dict()},
                            message='Website created', status_code=201)


@websites_bp.route('/<int:website_id>', methods=['GET'])
@jwt_required_custom
def get_website(website_id):
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)
    if website.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)
    return success_response(data={'website': website.to_dict()})


@websites_bp.route('/<int:website_id>', methods=['PUT'])
@jwt_required_custom
def update_website(website_id):
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)
    if website.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)

    data    = request.get_json(silent=True) or {}
    allowed = {k: v for k, v in data.items()
               if k in ('name', 'description', 'custom_domain', 'template')}
    if not allowed:
        return error_response('No valid fields to update', 400)

    website.update(**allowed)
    AuditLog.create_log(user_id=g.current_user.id, action='UPDATE',
                        resource_model='Website', resource_id=website_id)
    return success_response(data={'website': website.to_dict()}, message='Website updated')


@websites_bp.route('/<int:website_id>', methods=['DELETE'])
@jwt_required_custom
def delete_website(website_id):
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)
    if website.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)

    website.delete()
    AuditLog.create_log(user_id=g.current_user.id, action='DELETE',
                        resource_model='Website', resource_id=website_id)
    return success_response(message='Website deleted')


@websites_bp.route('/<int:website_id>/publish', methods=['PUT'])
@jwt_required_custom
def publish_website(website_id):
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)
    if website.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)

    website.publish()
    AuditLog.create_log(user_id=g.current_user.id, action='PUBLISH',
                        resource_model='Website', resource_id=website_id)
    return success_response(data={'website': website.to_dict()}, message='Website published')


@websites_bp.route('/<int:website_id>/unpublish', methods=['PUT'])
@jwt_required_custom
def unpublish_website(website_id):
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)
    if website.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)

    website.unpublish()
    AuditLog.create_log(user_id=g.current_user.id, action='UNPUBLISH',
                        resource_model='Website', resource_id=website_id)
    return success_response(data={'website': website.to_dict()}, message='Website unpublished')


# ── Page routes ───────────────────────────────────────────────────────────────

@websites_bp.route('/<int:website_id>/pages', methods=['POST'])
@jwt_required_custom
def add_page(website_id):
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)
    if website.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)

    # Check page limit
    if g.current_user.role != 'admin':
        page_limit = PAGE_LIMITS.get(g.current_user.subscription_type, 5)
        if len(website.pages) >= page_limit:
            return error_response(
                f'Page limit reached ({page_limit}) for your '
                f'{g.current_user.subscription_type} plan.', 403)

    data    = request.get_json(silent=True)
    if not data:
        return error_response('Request body must be JSON', 400)
    missing = validate_required_fields(data, ['title', 'slug'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    page = website.add_page(data['title'], data['slug'], data.get('content', ''))
    return success_response(data={'page': page.to_dict()},
                            message='Page added', status_code=201)


@websites_bp.route('/<int:website_id>/pages/<int:page_id>', methods=['PUT'])
@jwt_required_custom
def update_page(website_id, page_id):
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)
    if website.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)

    data = request.get_json(silent=True) or {}
    page = website.update_page(page_id, **data)
    if not page:
        return error_response('Page not found', 404)
    return success_response(data={'page': page.to_dict()}, message='Page updated')


@websites_bp.route('/<int:website_id>/pages/<int:page_id>', methods=['DELETE'])
@jwt_required_custom
def delete_page(website_id, page_id):
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)
    if website.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)

    if not website.delete_page(page_id):
        return error_response('Page not found', 404)
    return success_response(message='Page deleted')


# ── Admin route ───────────────────────────────────────────────────────────────

@websites_bp.route('/all', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_all_websites():
    page, limit, _ = get_pagination_params()
    search             = request.args.get('search')
    moderation_status  = request.args.get('moderationStatus')
    items, total       = Website.find_all(page=page, limit=limit,
                                          search=search,
                                          moderation_status=moderation_status)
    return paginated_response([w.to_dict() for w in items], total, page, limit)