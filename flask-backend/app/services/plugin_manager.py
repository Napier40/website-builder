"""
Plugin Manager Service
Singleton service for managing the plugin lifecycle in Flask
"""
import importlib
import importlib.util
import logging
import os
import sys
from app.models.plugin import PluginModel

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Singleton Plugin Manager.
    Handles plugin loading, initialization, and hook execution.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._hooks = {}           # hook_name -> list of callables
            self._loaded_plugins = {}  # plugin_name -> module
            PluginManager._initialized = True

    # ─── Initialization ───────────────────────────────────────────────────────

    def initialize(self, plugins_dir: str = None):
        """Load all active plugins from the database."""
        try:
            active_plugins = PluginModel.find_all({'isActive': True})
            logger.info(f"Initializing {len(active_plugins)} active plugin(s)...")

            for plugin in active_plugins:
                try:
                    self._load_plugin(plugin, plugins_dir)
                except Exception as e:
                    logger.error(f"Failed to load plugin '{plugin.get('name')}': {e}")

            logger.info(f"✅ Plugin manager initialized with {len(self._loaded_plugins)} plugin(s).")
        except Exception as e:
            logger.warning(f"Plugin manager initialization skipped: {e}")

    def _load_plugin(self, plugin: dict, plugins_dir: str = None):
        """Dynamically load a plugin module."""
        name = plugin.get('name')
        entry_point = plugin.get('entryPoint', '')

        if not entry_point:
            logger.warning(f"Plugin '{name}' has no entry point defined.")
            return

        # Resolve plugins directory
        if plugins_dir is None:
            plugins_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'plugins'
            )

        module_path = os.path.join(plugins_dir, entry_point)
        if not os.path.exists(module_path):
            logger.warning(f"Plugin entry point not found: {module_path}")
            return

        spec = importlib.util.spec_from_file_location(f"plugin_{name}", module_path)
        if spec is None:
            logger.warning(f"Could not create module spec for plugin '{name}'")
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._loaded_plugins[name] = module

        # Register hooks if the plugin defines them
        if hasattr(module, 'HOOKS'):
            for hook_name, handler in module.HOOKS.items():
                self.register_hook(hook_name, handler)
                logger.info(f"  Hook '{hook_name}' registered from plugin '{name}'")

        # Call plugin's setup function if it exists
        if hasattr(module, 'setup'):
            module.setup(plugin.get('settings', {}))

        logger.info(f"  ✅ Plugin '{name}' loaded successfully.")

    # ─── Hook system ─────────────────────────────────────────────────────────

    def register_hook(self, hook_name: str, handler):
        """Register a callable for a specific hook."""
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(handler)

    def execute_hook(self, hook_name: str, data: dict = None) -> dict:
        """
        Execute all handlers registered for a hook.
        Handlers can modify and return the data dict.
        Returns the (possibly modified) data.
        """
        handlers = self._hooks.get(hook_name, [])
        result = data or {}

        for handler in handlers:
            try:
                modified = handler(result)
                if modified is not None:
                    result = modified
            except Exception as e:
                logger.error(f"Hook '{hook_name}' handler raised an error: {e}")

        return result

    def get_registered_hooks(self) -> list:
        """Return names of all registered hooks."""
        return list(self._hooks.keys())

    def get_loaded_plugins(self) -> list:
        """Return names of all loaded plugins."""
        return list(self._loaded_plugins.keys())

    def reload_plugin(self, plugin_name: str, plugins_dir: str = None):
        """Reload a specific plugin (e.g. after settings change)."""
        # Unload first
        if plugin_name in self._loaded_plugins:
            module = self._loaded_plugins.pop(plugin_name)
            # Deregister its hooks
            if hasattr(module, 'HOOKS'):
                for hook_name in module.HOOKS:
                    if hook_name in self._hooks:
                        self._hooks[hook_name] = [
                            h for h in self._hooks[hook_name]
                            if h not in module.HOOKS.values()
                        ]

        # Reload from DB
        plugin = PluginModel.find_by_name(plugin_name)
        if plugin and plugin.get('isActive'):
            self._load_plugin(plugin, plugins_dir)


# Singleton instance
plugin_manager = PluginManager()