"""
Templates Blueprint
Routes: /api/templates - template CRUD, categories, save-as-template
"""
import logging
from flask import Blueprint, request, jsonify, g

from app.models.template import TemplateModel
from app.models.website import WebsiteModel
from app.middleware.auth import jwt_required_custom, authorize
from app.utils.helpers import (
    error_response, paginated_response, get_pagination_params,
    get_sort_params, validate_object_id
)

logger = logging.getLogger(__name__)
templates_bp = Blueprint('templates', __name__)


@templates_bp.route('', methods=['GET'])
def get_templates():
    """
    Get all public templates (with optional filters).
    GET /api/templates
    Query: category, isPremium, page, limit, sort
    """
    page, limit, skip = get_pagination_params()
    sort_field, sort_dir = get_sort_params('usageCount')

    query = {'isPublic': True}

    category = request.args.get('category', '').strip()
    if category:
        query['category'] = category

    is_premium = request.args.get('isPremium')
    if is_premium is not None:
        query['isPremium'] = is_premium.lower() == 'true'

    search = request.args.get('search', '').strip()
    if search:
        query['$or'] = [
            {'displayName': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}},
            {'tags': {'$in': [search.lower()]}}
        ]

    templates, total = TemplateModel.find_all(query, skip, limit, sort_field, sort_dir)
    return paginated_response(templates, total, page, limit)


@templates_bp.route('/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific template. GET /api/templates/<template_id>"""
    if not validate_object_id(template_id):
        return error_response('Invalid template ID format', 400)

    template = TemplateModel.find_by_id(template_id)
    if not template:
        return error_response('Template not found', 404)

    return jsonify({'success': True, 'template': template}), 200


@templates_bp.route('', methods=['POST'])
@jwt_required_custom
@authorize('admin')
def create_template():
    """
    Create a new template (admin only).
    POST /api/templates
    Body: { name, displayName, description, category, content?, settings?,
            tags?, isPremium?, isPublic?, thumbnail?, previewUrl? }
    """
    data = request.get_json() or {}
    required = ['name', 'displayName', 'description', 'category']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    try:
        template = TemplateModel.create(
            name=data['name'],
            display_name=data['displayName'],
            description=data['description'],
            category=data['category'],
            thumbnail=data.get('thumbnail'),
            preview_url=data.get('previewUrl'),
            content=data.get('content', {}),
            settings=data.get('settings', {}),
            tags=data.get('tags', []),
            is_premium=data.get('isPremium', False),
            is_public=data.get('isPublic', True),
            created_by=g.user_id
        )
        return jsonify({'success': True, 'template': template}), 201
    except Exception as e:
        logger.error(f"Create template error: {e}")
        return error_response('Server error creating template', 500)


@templates_bp.route('/<template_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_template(template_id):
    """Update a template. PUT /api/templates/<template_id>"""
    if not validate_object_id(template_id):
        return error_response('Invalid template ID format', 400)

    data = request.get_json() or {}
    allowed = ['displayName', 'description', 'category', 'content', 'settings',
               'tags', 'isPremium', 'isPublic', 'thumbnail', 'previewUrl']
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return error_response('No valid fields to update', 400)

    template = TemplateModel.update_by_id(template_id, updates)
    if not template:
        return error_response('Template not found', 404)

    return jsonify({'success': True, 'template': template}), 200


@templates_bp.route('/<template_id>', methods=['DELETE'])
@jwt_required_custom
@authorize('admin')
def delete_template(template_id):
    """Delete a template. DELETE /api/templates/<template_id>"""
    if not validate_object_id(template_id):
        return error_response('Invalid template ID format', 400)

    template = TemplateModel.find_by_id(template_id)
    if not template:
        return error_response('Template not found', 404)

    TemplateModel.delete_by_id(template_id)
    return jsonify({
        'success': True,
        'message': f"Template '{template.get('displayName')}' deleted successfully"
    }), 200


@templates_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all template categories. GET /api/templates/categories"""
    categories = TemplateModel.get_categories()
    valid_categories = TemplateModel.VALID_CATEGORIES
    return jsonify({
        'success': True,
        'categories': categories,
        'allCategories': valid_categories
    }), 200


@templates_bp.route('/tags', methods=['GET'])
def get_tags():
    """Get all template tags. GET /api/templates/tags"""
    tags = TemplateModel.get_tags()
    return jsonify({'success': True, 'tags': tags}), 200


@templates_bp.route('/save-from-website/<website_id>', methods=['POST'])
@jwt_required_custom
def save_as_template(website_id):
    """
    Save an existing website as a reusable template.
    POST /api/templates/save-from-website/<website_id>
    Body: { name, displayName, description, category, tags?, isPublic? }
    """
    if not validate_object_id(website_id):
        return error_response('Invalid website ID format', 400)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    # Only owner or admin can save as template
    if (str(website.get('user')) != g.user_id and
            g.current_user.get('role') != 'admin'):
        return error_response('Not authorized', 403)

    data = request.get_json() or {}
    required = ['name', 'displayName', 'description', 'category']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    try:
        template = TemplateModel.create(
            name=data['name'],
            display_name=data['displayName'],
            description=data['description'],
            category=data['category'],
            content={'pages': website.get('pages', [])},
            settings=website.get('settings', {}),
            tags=data.get('tags', []),
            is_premium=False,
            is_public=data.get('isPublic', False),  # private by default
            created_by=g.user_id
        )
        return jsonify({
            'success': True,
            'message': 'Website saved as template successfully',
            'template': template
        }), 201
    except Exception as e:
        logger.error(f"Save as template error: {e}")
        return error_response('Server error saving template', 500)


@templates_bp.route('/<template_id>/apply/<website_id>', methods=['PUT'])
@jwt_required_custom
def apply_template(template_id, website_id):
    """
    Apply a template to an existing website.
    PUT /api/templates/<template_id>/apply/<website_id>
    """
    if not validate_object_id(template_id) or not validate_object_id(website_id):
        return error_response('Invalid ID format', 400)

    template = TemplateModel.find_by_id(template_id)
    if not template:
        return error_response('Template not found', 404)

    website = WebsiteModel.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)

    if (str(website.get('user')) != g.user_id and
            g.current_user.get('role') != 'admin'):
        return error_response('Not authorized', 403)

    # Apply template content and settings
    updates = {'template': template.get('name', template_id)}
    if template.get('settings'):
        updates['settings'] = template['settings']

    updated_website = WebsiteModel.update_by_id(website_id, updates)
    TemplateModel.increment_usage(template_id)

    return jsonify({
        'success': True,
        'message': f"Template '{template.get('displayName')}' applied successfully",
        'website': updated_website
    }), 200