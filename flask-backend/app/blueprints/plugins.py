"""
Plugins Blueprint
"""
from flask import Blueprint, request, g

from app.models.plugin    import Plugin
from app.middleware.auth  import jwt_required_custom, authorize
from app.utils.helpers    import (success_response, error_response,
                                   validate_required_fields)

plugins_bp = Blueprint('plugins', __name__)


@plugins_bp.route('/', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_plugins():
    active_only = request.args.get('active', '').lower() == 'true'
    plugins     = Plugin.find_all(active_only=active_only)
    return success_response(data={'plugins': [p.to_dict() for p in plugins]})


@plugins_bp.route('/', methods=['POST'])
@jwt_required_custom
@authorize('admin')
def create_plugin():
    data    = request.get_json(silent=True) or {}
    missing = validate_required_fields(data, ['name', 'displayName'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    try:
        plugin = Plugin.create(
            name=data['name'],
            display_name=data['displayName'],
            description=data.get('description'),
            version=data.get('version', '1.0.0'),
            author=data.get('author'),
            config=data.get('config', {}),
            hooks=data.get('hooks', []),
        )
    except Exception as e:
        return error_response(f'Failed to create plugin: {e}', 500)

    return success_response(data={'plugin': plugin.to_dict()},
                            message='Plugin created', status_code=201)


@plugins_bp.route('/<int:plugin_id>', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_plugin(plugin_id):
    plugin = Plugin.find_by_id(plugin_id)
    if not plugin:
        return error_response('Plugin not found', 404)
    return success_response(data={'plugin': plugin.to_dict()})


@plugins_bp.route('/<int:plugin_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_plugin(plugin_id):
    plugin = Plugin.find_by_id(plugin_id)
    if not plugin:
        return error_response('Plugin not found', 404)

    data    = request.get_json(silent=True) or {}
    allowed = {k: v for k, v in data.items()
               if k in ('display_name', 'description', 'version',
                        'author', 'is_active', 'config', 'hooks')}
    plugin.update(**allowed)
    return success_response(data={'plugin': plugin.to_dict()}, message='Plugin updated')


@plugins_bp.route('/<int:plugin_id>', methods=['DELETE'])
@jwt_required_custom
@authorize('admin')
def delete_plugin(plugin_id):
    plugin = Plugin.find_by_id(plugin_id)
    if not plugin:
        return error_response('Plugin not found', 404)
    plugin.delete()
    return success_response(message='Plugin deleted')


@plugins_bp.route('/<int:plugin_id>/toggle', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def toggle_plugin(plugin_id):
    plugin = Plugin.find_by_id(plugin_id)
    if not plugin:
        return error_response('Plugin not found', 404)
    new_state = plugin.toggle_active()
    return success_response(
        data={'plugin': plugin.to_dict()},
        message=f"Plugin {'activated' if new_state else 'deactivated'}",
    )