const Plugin = require('../models/Plugin');
const pluginManager = require('../services/pluginManager');
const ErrorResponse = require('../utils/errorResponse');
const asyncHandler = require('../middleware/async');
const AuditLog = require('../models/AuditLog');
const path = require('path');
const fs = require('fs');

// @desc    Get all plugins
// @route   GET /api/plugins
// @access  Private/Admin
exports.getPlugins = asyncHandler(async (req, res, next) => {
  const { active } = req.query;
  const activeOnly = active === 'true';
  
  const plugins = await pluginManager.getPlugins(activeOnly);
  
  res.status(200).json({
    success: true,
    count: plugins.length,
    data: plugins
  });
});

// @desc    Get plugin by ID
// @route   GET /api/plugins/:id
// @access  Private/Admin
exports.getPluginById = asyncHandler(async (req, res, next) => {
  const plugin = await Plugin.findById(req.params.id);
  
  if (!plugin) {
    return next(new ErrorResponse(`Plugin not found with id of ${req.params.id}`, 404));
  }
  
  res.status(200).json({
    success: true,
    data: plugin
  });
});

// @desc    Register a new plugin
// @route   POST /api/plugins
// @access  Private/Admin
exports.registerPlugin = asyncHandler(async (req, res, next) => {
  // Add the installing user
  req.body.installedBy = req.user._id;
  
  // Check if plugin with this name already exists
  const existingPlugin = await Plugin.findOne({ name: req.body.name });
  if (existingPlugin) {
    return next(new ErrorResponse(`Plugin with name ${req.body.name} already exists`, 400));
  }
  
  // Register the plugin
  const plugin = await pluginManager.registerPlugin(req.body);
  
  // Create audit log
  await AuditLog.createLog({
    user: req.user._id,
    action: 'ADMIN_ACTION',
    resource: `/api/plugins`,
    resourceId: plugin._id,
    resourceModel: 'Plugin',
    details: { 
      action: 'REGISTER_PLUGIN',
      pluginName: plugin.name
    }
  });
  
  res.status(201).json({
    success: true,
    data: plugin
  });
});

// @desc    Update plugin settings
// @route   PUT /api/plugins/:id/settings
// @access  Private/Admin
exports.updatePluginSettings = asyncHandler(async (req, res, next) => {
  const plugin = await Plugin.findById(req.params.id);
  
  if (!plugin) {
    return next(new ErrorResponse(`Plugin not found with id of ${req.params.id}`, 404));
  }
  
  // Store original settings for audit log
  const originalSettings = { ...plugin.settings };
  
  // Update plugin settings
  const updatedPlugin = await pluginManager.updatePluginSettings(plugin.name, req.body);
  
  // Create audit log
  await AuditLog.createLog({
    user: req.user._id,
    action: 'ADMIN_ACTION',
    resource: `/api/plugins/${plugin._id}/settings`,
    resourceId: plugin._id,
    resourceModel: 'Plugin',
    previousState: { settings: originalSettings },
    newState: { settings: updatedPlugin.settings },
    details: { 
      action: 'UPDATE_PLUGIN_SETTINGS',
      pluginName: plugin.name
    }
  });
  
  res.status(200).json({
    success: true,
    data: updatedPlugin
  });
});

// @desc    Toggle plugin active state
// @route   PUT /api/plugins/:id/toggle
// @access  Private/Admin
exports.togglePluginActive = asyncHandler(async (req, res, next) => {
  const { isActive } = req.body;
  
  if (isActive === undefined) {
    return next(new ErrorResponse('Please provide isActive field', 400));
  }
  
  const plugin = await Plugin.findById(req.params.id);
  
  if (!plugin) {
    return next(new ErrorResponse(`Plugin not found with id of ${req.params.id}`, 404));
  }
  
  // Toggle plugin active state
  const updatedPlugin = await pluginManager.togglePluginActive(plugin.name, isActive);
  
  // Create audit log
  await AuditLog.createLog({
    user: req.user._id,
    action: 'ADMIN_ACTION',
    resource: `/api/plugins/${plugin._id}/toggle`,
    resourceId: plugin._id,
    resourceModel: 'Plugin',
    previousState: { isActive: plugin.isActive },
    newState: { isActive: updatedPlugin.isActive },
    details: { 
      action: isActive ? 'ACTIVATE_PLUGIN' : 'DEACTIVATE_PLUGIN',
      pluginName: plugin.name
    }
  });
  
  res.status(200).json({
    success: true,
    data: updatedPlugin
  });
});

// @desc    Delete plugin
// @route   DELETE /api/plugins/:id
// @access  Private/Admin
exports.deletePlugin = asyncHandler(async (req, res, next) => {
  const plugin = await Plugin.findById(req.params.id);
  
  if (!plugin) {
    return next(new ErrorResponse(`Plugin not found with id of ${req.params.id}`, 404));
  }
  
  // Unload plugin if it's active
  if (plugin.isActive) {
    await pluginManager.unloadPlugin(plugin.name);
  }
  
  // Create audit log before deletion
  await AuditLog.createLog({
    user: req.user._id,
    action: 'ADMIN_ACTION',
    resource: `/api/plugins/${plugin._id}`,
    resourceId: plugin._id,
    resourceModel: 'Plugin',
    previousState: plugin.toObject(),
    details: { 
      action: 'DELETE_PLUGIN',
      pluginName: plugin.name
    }
  });
  
  // Delete plugin
  await plugin.remove();
  
  res.status(200).json({
    success: true,
    data: {}
  });
});

// @desc    Upload plugin file
// @route   POST /api/plugins/upload
// @access  Private/Admin
exports.uploadPlugin = asyncHandler(async (req, res, next) => {
  if (!req.files || !req.files.plugin) {
    return next(new ErrorResponse('Please upload a plugin file', 400));
  }
  
  const pluginFile = req.files.plugin;
  
  // Check if it's a JavaScript file
  if (!pluginFile.name.endsWith('.js')) {
    return next(new ErrorResponse('Please upload a valid JavaScript plugin file', 400));
  }
  
  // Create plugins directory if it doesn't exist
  const pluginsDir = path.join(__dirname, '../plugins');
  if (!fs.existsSync(pluginsDir)) {
    fs.mkdirSync(pluginsDir, { recursive: true });
  }
  
  // Save the file
  const fileName = `${Date.now()}-${pluginFile.name}`;
  const filePath = path.join(pluginsDir, fileName);
  
  await pluginFile.mv(filePath);
  
  // Create audit log
  await AuditLog.createLog({
    user: req.user._id,
    action: 'ADMIN_ACTION',
    resource: `/api/plugins/upload`,
    details: { 
      action: 'UPLOAD_PLUGIN',
      fileName,
      originalName: pluginFile.name
    }
  });
  
  res.status(200).json({
    success: true,
    data: {
      fileName,
      filePath: `plugins/${fileName}`
    }
  });
});

// @desc    Execute plugin hook
// @route   POST /api/plugins/hook/:hookName
// @access  Private
exports.executeHook = asyncHandler(async (req, res, next) => {
  const { hookName } = req.params;
  
  // Execute the hook
  const results = await pluginManager.executeHook(hookName, {
    user: req.user,
    body: req.body,
    query: req.query
  });
  
  res.status(200).json({
    success: true,
    data: results
  });
});