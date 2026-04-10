"""
Websites Blueprint
Routes: /api/websites - CRUD, page management, publish/unpublish
"""
import logging
from flask import Blueprint, request, jsonify, g

from app.models.website import WebsiteModel
from app.models.user import UserModel
from app.models.subscription import SubscriptionModel
from app.models.audit_log import AuditLogModel
from app.middleware.auth import jwt_required_custom, authorize
from app.utils.helpers import (
    validate_required_fields, validate_subdomain, validate_object_id,
    error_response, paginated_response, get_pagination_params, get_sort_params
)

logger = logging.getLogger(__name__)
websites_bp = Blueprint('websites', __name__)


def _check_website_ownership(website: dict, user: dict) -> bool:
    """Return True if the user owns the website or is an admin."""
    return (str(website.get('user')) == str(user.get('_id'))
            or user.get('role') == 'admin')


# ─── Website CRUD ─────────────────────────────────────────────────────────────

@websites_bp.route('', methods=['GET'])
@jwt_required_custom
def get_my_websites():
    """
    Get all websites for the current user.
    GET /api/websites
    """
    websites = WebsiteModel.find_by_user(g.user_id)
    return jsonify({
        'success': True,
        'count': len(websites),
        'websites': websites
    }), 200


@websites_bp.route('/all', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_all_websites():
    """
    Admin: get all websites with pagination and filters.
    GET /api/websites/all
    """
    page, limit, skip = get_pagination_params()
    sort_field, sort_dir = get_sort_params('createdAt')
    query = {}

    if request.args.get('isPublished') is not None:
        query['isPublished'] = request.args.get('isPublished') == 'true'
    if request.args.get('moderationStatus'):
        query['moderationStatus'] = request.args.get('moderationStatus')

    websites, total = WebsiteModel.find_all(query, skip, limit, sort_field, sort_dir)
    return paginated_response(websites, total, page, limit)


@websites_bp.route('/<website_id>', methods=['GET'])
@jwt_required_custom
def get_website_by_id(website_id):
    """
    Get a specific website by ID.
    GET /api/websites/<website_id>
    """
    if not validate_object_id(website_id):
        return error_response('Invalid website ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    if not _check_website_ownership(website, g.current_user):
        return error_response('Not authorized to access this website', 403)

    return jsonify({'success': True, 'website': website}), 200


@websites_bp.route('', methods=['POST'])
@jwt_required_custom
def create_website():
    """
    Create a new website.
    POST /api/websites
    Body: { name, subdomain, template? }
    """
    data = request.get_json()
    if not data:
        return error_response('Request body must be JSON', 400)

    missing = validate_required_fields(data, ['name', 'subdomain'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    subdomain = data.get('subdomain', '').lower().strip()
    if not validate_subdomain(subdomain):
        return error_response(
            'Subdomain must be 3-63 characters, lowercase letters, digits, and hyphens only. '
            'Cannot start or end with a hyphen.', 400
        )

    # Check website limit based on subscription
    user = g.current_user
    current_count = WebsiteModel.count_by_user(g.user_id)
    website_limit = 1  # default free tier

    if user.get('subscriptionStatus') not in (None, 'none'):
        plan = SubscriptionModel.find_by_name(user['subscriptionStatus'])
        if plan:
            website_limit = plan.get('websiteLimit', 1)

    if current_count >= website_limit:
        return error_response(
            f"You have reached your website limit ({website_limit}). "
            f"Please upgrade your subscription to create more websites.", 403
        )

    try:
        website = WebsiteModel.create(
            name=data['name'],
            subdomain=subdomain,
            user_id=g.user_id,
            template=data.get('template', 'default')
        )

        AuditLogModel.create_log(
            user_id=g.user_id, action='CREATE',
            resource='/api/websites', resource_id=website['_id'],
            resource_model='Website',
            details={'name': website['name'], 'subdomain': website['subdomain']}
        )

        return jsonify({'success': True, 'website': website}), 201

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Create website error: {e}")
        return error_response('Server error creating website', 500)


@websites_bp.route('/<website_id>', methods=['PUT'])
@jwt_required_custom
def update_website(website_id):
    """
    Update a website's name, domain, template, or settings.
    PUT /api/websites/<website_id>
    """
    if not validate_object_id(website_id):
        return error_response('Invalid website ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    if not _check_website_ownership(website, g.current_user):
        return error_response('Not authorized to update this website', 403)

    data = request.get_json() or {}
    updates = {}

    if 'name' in data and data['name'].strip():
        updates['name'] = data['name'].strip()

    if 'customDomain' in data:
        custom_domain = data['customDomain']
        if custom_domain:
            user = g.current_user
            if user.get('role') != 'admin' and user.get('subscriptionStatus') in (None, 'none', 'basic'):
                return error_response(
                    'Custom domains are only available for Premium and Enterprise subscriptions', 403
                )
            if WebsiteModel.domain_exists(custom_domain, exclude_id=website_id):
                return error_response('This domain is already in use', 400)
        updates['customDomain'] = custom_domain

    if 'template' in data:
        updates['template'] = data['template']

    if 'settings' in data and isinstance(data['settings'], dict):
        existing_settings = website.get('settings', {})
        merged_settings = {**existing_settings, **data['settings']}
        updates['settings'] = merged_settings

    if not updates:
        return error_response('No valid fields to update', 400)

    updated = WebsiteModel.update_by_id(website_id, updates)
    return jsonify({'success': True, 'website': updated}), 200


@websites_bp.route('/<website_id>', methods=['DELETE'])
@jwt_required_custom
def delete_website(website_id):
    """
    Delete a website.
    DELETE /api/websites/<website_id>
    """
    if not validate_object_id(website_id):
        return error_response('Invalid website ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    if not _check_website_ownership(website, g.current_user):
        return error_response('Not authorized to delete this website', 403)

    AuditLogModel.create_log(
        user_id=g.user_id, action='DELETE',
        resource=f'/api/websites/{website_id}',
        resource_id=website_id, resource_model='Website',
        previous_state={'name': website.get('name'), 'subdomain': website.get('subdomain')},
        details={'action': 'DELETE_WEBSITE'}
    )

    WebsiteModel.delete_by_id(website_id)
    return jsonify({'success': True, 'message': 'Website deleted successfully'}), 200


# ─── Publish / Unpublish ──────────────────────────────────────────────────────

@websites_bp.route('/<website_id>/publish', methods=['PUT'])
@jwt_required_custom
def publish_website(website_id):
    """Publish a website. PUT /api/websites/<website_id>/publish"""
    if not validate_object_id(website_id):
        return error_response('Invalid website ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    if not _check_website_ownership(website, g.current_user):
        return error_response('Not authorized to publish this website', 403)

    if website.get('moderationStatus') == 'rejected':
        return error_response(
            'This website has been rejected by moderation and cannot be published.', 403
        )

    updated = WebsiteModel.publish(website_id)
    AuditLogModel.create_log(
        user_id=g.user_id, action='PUBLISH',
        resource=f'/api/websites/{website_id}/publish',
        resource_id=website_id, resource_model='Website'
    )
    return jsonify({'success': True, 'message': 'Website published successfully', 'website': updated}), 200


@websites_bp.route('/<website_id>/unpublish', methods=['PUT'])
@jwt_required_custom
def unpublish_website(website_id):
    """Unpublish a website. PUT /api/websites/<website_id>/unpublish"""
    if not validate_object_id(website_id):
        return error_response('Invalid website ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    if not _check_website_ownership(website, g.current_user):
        return error_response('Not authorized to unpublish this website', 403)

    updated = WebsiteModel.unpublish(website_id)
    AuditLogModel.create_log(
        user_id=g.user_id, action='UNPUBLISH',
        resource=f'/api/websites/{website_id}/unpublish',
        resource_id=website_id, resource_model='Website'
    )
    return jsonify({'success': True, 'message': 'Website unpublished successfully', 'website': updated}), 200


# ─── Page Management ──────────────────────────────────────────────────────────

@websites_bp.route('/<website_id>/pages', methods=['POST'])
@jwt_required_custom
def create_page(website_id):
    """
    Add a new page to a website.
    POST /api/websites/<website_id>/pages
    Body: { title, slug, content?, meta? }
    """
    if not validate_object_id(website_id):
        return error_response('Invalid website ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    if not _check_website_ownership(website, g.current_user):
        return error_response('Not authorized to update this website', 403)

    data = request.get_json() or {}
    missing = validate_required_fields(data, ['title', 'slug'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    # Check for duplicate slug
    existing_slugs = [p.get('slug') for p in website.get('pages', [])]
    if data['slug'].lower() in existing_slugs:
        return error_response('A page with this slug already exists', 400)

    page = WebsiteModel.add_page(website_id, {
        'title': data['title'],
        'slug': data['slug'].lower().strip(),
        'content': data.get('content', {}),
        'meta': data.get('meta', {})
    })

    return jsonify({'success': True, 'page': page}), 201


@websites_bp.route('/<website_id>/pages/<page_id>', methods=['PUT'])
@jwt_required_custom
def update_page(website_id, page_id):
    """
    Update a specific page within a website.
    PUT /api/websites/<website_id>/pages/<page_id>
    """
    if not validate_object_id(website_id) or not validate_object_id(page_id):
        return error_response('Invalid ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    if not _check_website_ownership(website, g.current_user):
        return error_response('Not authorized to update this website', 403)

    data = request.get_json() or {}
    allowed_fields = ['title', 'content', 'isPublished', 'meta']
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    if not updates:
        return error_response('No valid fields to update', 400)

    page = WebsiteModel.update_page(website_id, page_id, updates)
    if not page:
        return error_response('Page not found', 404)

    return jsonify({'success': True, 'page': page}), 200


@websites_bp.route('/<website_id>/pages/<page_id>', methods=['DELETE'])
@jwt_required_custom
def delete_page(website_id, page_id):
    """
    Delete a page from a website (cannot delete home page).
    DELETE /api/websites/<website_id>/pages/<page_id>
    """
    if not validate_object_id(website_id) or not validate_object_id(page_id):
        return error_response('Invalid ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    if not _check_website_ownership(website, g.current_user):
        return error_response('Not authorized to update this website', 403)

    # Prevent deletion of home page
    target_page = next((p for p in website.get('pages', []) if str(p.get('_id')) == page_id), None)
    if not target_page:
        return error_response('Page not found', 404)

    if target_page.get('slug') == 'home':
        return error_response('Cannot delete the home page', 400)

    deleted = WebsiteModel.delete_page(website_id, page_id)
    if not deleted:
        return error_response('Failed to delete page', 500)

    return jsonify({'success': True, 'message': 'Page deleted successfully'}), 200