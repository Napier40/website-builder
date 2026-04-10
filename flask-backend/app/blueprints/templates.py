"""
Templates Blueprint
"""
from flask import Blueprint, request, g

from app.models.template  import Template
from app.models.website   import Website
from app.models.audit_log import AuditLog
from app.middleware.auth  import jwt_required_custom, authorize
from app.utils.helpers    import (success_response, error_response,
                                   paginated_response, get_pagination_params,
                                   validate_required_fields)

templates_bp = Blueprint('templates', __name__)


@templates_bp.route('/', methods=['GET'])
def get_templates():
    page, limit, _ = get_pagination_params(default_limit=20)
    category   = request.args.get('category')
    search     = request.args.get('search')
    is_premium = request.args.get('isPremium')
    if is_premium is not None:
        is_premium = is_premium.lower() == 'true'

    items, total = Template.find_all(page=page, limit=limit,
                                     category=category, search=search,
                                     is_premium=is_premium if is_premium is not None else None)
    return paginated_response([t.to_dict() for t in items], total, page, limit)


@templates_bp.route('/categories', methods=['GET'])
def get_categories():
    return success_response(data={'categories': Template.get_categories()})


@templates_bp.route('/tags', methods=['GET'])
def get_tags():
    return success_response(data={'tags': Template.get_tags()})


@templates_bp.route('/<int:template_id>', methods=['GET'])
def get_template(template_id):
    template = Template.find_by_id(template_id)
    if not template:
        return error_response('Template not found', 404)
    return success_response(data={'template': template.to_dict()})


@templates_bp.route('/', methods=['POST'])
@jwt_required_custom
@authorize('admin')
def create_template():
    data    = request.get_json(silent=True) or {}
    missing = validate_required_fields(data, ['name', 'displayName', 'category'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    import json
    try:
        template = Template(
            name=data['name'].lower().strip(),
            display_name=data['displayName'],
            description=data.get('description', ''),
            category=data['category'],
            is_premium=data.get('isPremium', False),
            is_public=data.get('isPublic', True),
            tags=json.dumps(data.get('tags', [])),
            thumbnail_url=data.get('thumbnailUrl'),
            content=json.dumps(data.get('content', {})),
        )
        from app.database import db
        db.session.add(template)
        db.session.commit()
    except Exception as e:
        from app.database import db
        db.session.rollback()
        return error_response(f'Failed to create template: {e}', 500)

    return success_response(data={'template': template.to_dict()},
                            message='Template created', status_code=201)


@templates_bp.route('/<int:template_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_template(template_id):
    template = Template.find_by_id(template_id)
    if not template:
        return error_response('Template not found', 404)

    data    = request.get_json(silent=True) or {}
    allowed = {k: v for k, v in data.items()
               if k in ('display_name', 'description', 'category',
                        'is_premium', 'is_public', 'tags',
                        'thumbnail_url', 'content')}
    template.update(**allowed)
    return success_response(data={'template': template.to_dict()},
                            message='Template updated')


@templates_bp.route('/<int:template_id>', methods=['DELETE'])
@jwt_required_custom
@authorize('admin')
def delete_template(template_id):
    template = Template.find_by_id(template_id)
    if not template:
        return error_response('Template not found', 404)
    template.delete()
    return success_response(message='Template deleted')


@templates_bp.route('/apply/<int:template_id>/to/<int:website_id>', methods=['PUT'])
@jwt_required_custom
def apply_template(template_id, website_id):
    template = Template.find_by_id(template_id)
    if not template:
        return error_response('Template not found', 404)

    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)
    if website.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)

    # Apply template: update the website's template field
    website.update(template=template.name)
    template.increment_usage()

    AuditLog.create_log(user_id=g.current_user.id, action='UPDATE',
                        resource_model='Website', resource_id=website_id,
                        description=f'Applied template {template.name}')
    return success_response(
        data={'website': website.to_dict()},
        message=f"Template '{template.display_name}' applied to website",
    )