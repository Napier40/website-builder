const Plugin = require('../models/Plugin');
const path = require('path');
const fs = require('fs');

/**
 * Plugin Manager Service
 * Handles loading, registering, and executing plugins
 */
class PluginManager {
  constructor() {
    this.loadedPlugins = new Map();
    this.pluginsDir = path.join(__dirname, '../plugins');
    
    // Create plugins directory if it doesn't exist
    if (!fs.existsSync(this.pluginsDir)) {
      fs.mkdirSync(this.pluginsDir, { recursive: true });
    }
  }
  
  /**
   * Initialize the plugin manager
   * Loads all active plugins from the database
   */
  async initialize() {
    try {
      const activePlugins = await Plugin.find({ isActive: true });
      
      for (const plugin of activePlugins) {
        await this.loadPlugin(plugin.name);
      }
      
      console.log(`Initialized ${this.loadedPlugins.size} plugins`);
    } catch (error) {
      console.error('Error initializing plugin manager:', error);
    }
  }
  
  /**
   * Load a plugin by name
   * @param {string} pluginName - The name of the plugin to load
   * @returns {Object|null} - The loaded plugin or null if not found
   */
  async loadPlugin(pluginName) {
    try {
      // Check if plugin is already loaded
      if (this.loadedPlugins.has(pluginName)) {
        return this.loadedPlugins.get(pluginName);
      }
      
      // Get plugin from database
      const plugin = await Plugin.findOne({ name: pluginName, isActive: true });
      if (!plugin) {
        console.error(`Plugin ${pluginName} not found or not active`);
        return null;
      }
      
      // Determine plugin path
      let pluginPath;
      if (plugin.entryPoint.startsWith('http')) {
        // External plugin (not implemented in this example)
        console.error('External plugins not supported yet');
        return null;
      } else {
        // Local plugin
        pluginPath = path.join(this.pluginsDir, plugin.entryPoint);
        
        // Check if plugin file exists
        if (!fs.existsSync(pluginPath)) {
          console.error(`Plugin file not found: ${pluginPath}`);
          return null;
        }
      }
      
      // Load plugin module
      const pluginModule = require(pluginPath);
      
      // Initialize plugin if it has an init function
      if (typeof pluginModule.init === 'function') {
        await pluginModule.init(plugin.settings);
      }
      
      // Store loaded plugin
      const loadedPlugin = {
        ...pluginModule,
        metadata: plugin,
        settings: plugin.settings
      };
      
      this.loadedPlugins.set(pluginName, loadedPlugin);
      console.log(`Plugin ${pluginName} loaded successfully`);
      
      return loadedPlugin;
    } catch (error) {
      console.error(`Error loading plugin ${pluginName}:`, error);
      return null;
    }
  }
  
  /**
   * Unload a plugin by name
   * @param {string} pluginName - The name of the plugin to unload
   * @returns {boolean} - Whether the plugin was successfully unloaded
   */
  async unloadPlugin(pluginName) {
    try {
      const plugin = this.loadedPlugins.get(pluginName);
      
      if (!plugin) {
        return false;
      }
      
      // Call cleanup function if it exists
      if (typeof plugin.cleanup === 'function') {
        await plugin.cleanup();
      }
      
      // Remove from loaded plugins
      this.loadedPlugins.delete(pluginName);
      
      // Clear require cache to allow reloading
      if (plugin.metadata && plugin.metadata.entryPoint) {
        const pluginPath = path.join(this.pluginsDir, plugin.metadata.entryPoint);
        delete require.cache[require.resolve(pluginPath)];
      }
      
      console.log(`Plugin ${pluginName} unloaded successfully`);
      return true;
    } catch (error) {
      console.error(`Error unloading plugin ${pluginName}:`, error);
      return false;
    }
  }
  
  /**
   * Execute a hook across all plugins
   * @param {string} hookName - The name of the hook to execute
   * @param {Object} context - The context to pass to the hook
   * @returns {Array} - Array of results from all plugins that implemented the hook
   */
  async executeHook(hookName, context = {}) {
    const results = [];
    
    for (const [pluginName, plugin] of this.loadedPlugins.entries()) {
      try {
        if (typeof plugin[hookName] === 'function') {
          const result = await plugin[hookName](context, plugin.settings);
          results.push({
            plugin: pluginName,
            result
          });
        }
      } catch (error) {
        console.error(`Error executing hook ${hookName} in plugin ${pluginName}:`, error);
        results.push({
          plugin: pluginName,
          error: error.message
        });
      }
    }
    
    return results;
  }
  
  /**
   * Register a new plugin
   * @param {Object} pluginData - Plugin data
   * @returns {Object} - The registered plugin
   */
  async registerPlugin(pluginData) {
    try {
      // Create plugin in database
      const plugin = await Plugin.create(pluginData);
      
      // Load the plugin if it's active
      if (plugin.isActive) {
        await this.loadPlugin(plugin.name);
      }
      
      return plugin;
    } catch (error) {
      console.error('Error registering plugin:', error);
      throw error;
    }
  }
  
  /**
   * Update plugin settings
   * @param {string} pluginName - The name of the plugin
   * @param {Object} settings - New settings
   * @returns {Object} - The updated plugin
   */
  async updatePluginSettings(pluginName, settings) {
    try {
      // Update plugin in database
      const plugin = await Plugin.findOneAndUpdate(
        { name: pluginName },
        { settings, lastUpdated: Date.now() },
        { new: true }
      );
      
      if (!plugin) {
        throw new Error(`Plugin ${pluginName} not found`);
      }
      
      // Reload plugin if it's active
      if (plugin.isActive) {
        await this.unloadPlugin(pluginName);
        await this.loadPlugin(pluginName);
      }
      
      return plugin;
    } catch (error) {
      console.error(`Error updating plugin ${pluginName} settings:`, error);
      throw error;
    }
  }
  
  /**
   * Toggle plugin active state
   * @param {string} pluginName - The name of the plugin
   * @param {boolean} isActive - Whether the plugin should be active
   * @returns {Object} - The updated plugin
   */
  async togglePluginActive(pluginName, isActive) {
    try {
      // Update plugin in database
      const plugin = await Plugin.findOneAndUpdate(
        { name: pluginName },
        { isActive, lastUpdated: Date.now() },
        { new: true }
      );
      
      if (!plugin) {
        throw new Error(`Plugin ${pluginName} not found`);
      }
      
      // Load or unload plugin based on new state
      if (isActive) {
        await this.loadPlugin(pluginName);
      } else {
        await this.unloadPlugin(pluginName);
      }
      
      return plugin;
    } catch (error) {
      console.error(`Error toggling plugin ${pluginName} active state:`, error);
      throw error;
    }
  }
  
  /**
   * Get all registered plugins
   * @param {boolean} activeOnly - Whether to return only active plugins
   * @returns {Array} - Array of plugins
   */
  async getPlugins(activeOnly = false) {
    try {
      const query = activeOnly ? { isActive: true } : {};
      return await Plugin.find(query).sort({ name: 1 });
    } catch (error) {
      console.error('Error getting plugins:', error);
      throw error;
    }
  }
}

// Create singleton instance
const pluginManager = new PluginManager();

module.exports = pluginManager;