"""
Plugins Blueprint
Routes: /api/plugins - plugin registry, settings, toggle, hooks
"""
import logging
from flask import Blueprint, request, jsonify, g

from app.models.plugin import PluginModel
from app.middleware.auth import jwt_required_custom, authorize
from app.utils.helpers import error_response, validate_object_id

logger = logging.getLogger(__name__)
plugins_bp = Blueprint('plugins', __name__)


@plugins_bp.route('', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_plugins():
    """Get all registered plugins. GET /api/plugins"""
    is_active = request.args.get('isActive')
    query = {}
    if is_active is not None:
        query['isActive'] = is_active.lower() == 'true'

    plugins = PluginModel.find_all(query)
    return jsonify({'success': True, 'count': len(plugins), 'plugins': plugins}), 200


@plugins_bp.route('/<plugin_id>', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_plugin(plugin_id):
    """Get a specific plugin by ID. GET /api/plugins/<plugin_id>"""
    if not validate_object_id(plugin_id):
        return error_response('Invalid plugin ID format', 400)

    plugin = PluginModel.find_by_id(plugin_id)
    if not plugin:
        return error_response('Plugin not found', 404)

    return jsonify({'success': True, 'plugin': plugin}), 200


@plugins_bp.route('', methods=['POST'])
@jwt_required_custom
@authorize('admin')
def register_plugin():
    """
    Register a new plugin.
    POST /api/plugins
    Body: { name, displayName, description, version, author, entryPoint, hooks?, settings? }
    """
    data = request.get_json() or {}
    required = ['name', 'displayName', 'description', 'version', 'author', 'entryPoint']

    missing = [f for f in required if not data.get(f)]
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    try:
        plugin = PluginModel.create(
            name=data['name'],
            display_name=data['displayName'],
            description=data['description'],
            version=data['version'],
            author=data['author'],
            entry_point=data['entryPoint'],
            hooks=data.get('hooks', []),
            settings=data.get('settings', {})
        )
        return jsonify({'success': True, 'plugin': plugin}), 201
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Register plugin error: {e}")
        return error_response('Server error registering plugin', 500)


@plugins_bp.route('/<plugin_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_plugin(plugin_id):
    """Update a plugin's settings. PUT /api/plugins/<plugin_id>"""
    if not validate_object_id(plugin_id):
        return error_response('Invalid plugin ID format', 400)

    data = request.get_json() or {}
    allowed = ['displayName', 'description', 'version', 'settings', 'hooks']
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return error_response('No valid fields to update', 400)

    plugin = PluginModel.update_by_id(plugin_id, updates)
    if not plugin:
        return error_response('Plugin not found', 404)

    return jsonify({'success': True, 'plugin': plugin}), 200


@plugins_bp.route('/<plugin_id>/toggle', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def toggle_plugin(plugin_id):
    """
    Toggle a plugin's active state and reload it if activated.
    PUT /api/plugins/<plugin_id>/toggle
    """
    if not validate_object_id(plugin_id):
        return error_response('Invalid plugin ID format', 400)

    plugin = PluginModel.toggle_active(plugin_id)
    if not plugin:
        return error_response('Plugin not found', 404)

    # Reload via plugin manager when activated
    if plugin.get('isActive'):
        try:
            from app.services.plugin_manager import plugin_manager
            plugin_manager.reload_plugin(plugin.get('name'))
        except Exception as e:
            logger.warning(f"Plugin reload failed (non-critical): {e}")

    state = 'activated' if plugin.get('isActive') else 'deactivated'
    return jsonify({
        'success': True,
        'message': f"Plugin '{plugin.get('displayName')}' {state} successfully",
        'plugin': plugin
    }), 200


@plugins_bp.route('/<plugin_id>', methods=['DELETE'])
@jwt_required_custom
@authorize('admin')
def delete_plugin(plugin_id):
    """Delete a plugin registration. DELETE /api/plugins/<plugin_id>"""
    if not validate_object_id(plugin_id):
        return error_response('Invalid plugin ID format', 400)

    plugin = PluginModel.find_by_id(plugin_id)
    if not plugin:
        return error_response('Plugin not found', 404)

    PluginModel.delete_by_id(plugin_id)
    return jsonify({
        'success': True,
        'message': f"Plugin '{plugin.get('displayName')}' removed successfully"
    }), 200


@plugins_bp.route('/hooks/<hook_name>/execute', methods=['POST'])
@jwt_required_custom
@authorize('admin')
def execute_hook(hook_name):
    """
    Execute a registered plugin hook.
    POST /api/plugins/hooks/<hook_name>/execute
    Body: { data? }
    """
    data = request.get_json() or {}
    hook_data = data.get('data', {})

    try:
        from app.services.plugin_manager import plugin_manager
        result = plugin_manager.execute_hook(hook_name, hook_data)
        return jsonify({
            'success': True,
            'hookName': hook_name,
            'result': result
        }), 200
    except Exception as e:
        logger.error(f"Hook execution error: {e}")
        return error_response(f'Error executing hook: {str(e)}', 500)


@plugins_bp.route('/hooks', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_registered_hooks():
    """List all registered hooks. GET /api/plugins/hooks"""
    from app.services.plugin_manager import plugin_manager
    hooks = plugin_manager.get_registered_hooks()
    loaded = plugin_manager.get_loaded_plugins()
    return jsonify({
        'success': True,
        'hooks': hooks,
        'loadedPlugins': loaded
    }), 200