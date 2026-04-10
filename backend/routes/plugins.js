const express = require('express');
const router = express.Router();
const {
  getPlugins,
  getPluginById,
  registerPlugin,
  updatePluginSettings,
  togglePluginActive,
  deletePlugin,
  uploadPlugin,
  executeHook
} = require('../controllers/pluginController');

const { protect, authorize } = require('../middleware/auth');
const auditLogger = require('../middleware/auditLogger');

// Admin-only routes
router.get('/', protect, authorize('admin'), auditLogger('ADMIN_ACTION'), getPlugins);
router.get('/:id', protect, authorize('admin'), auditLogger('ADMIN_ACTION'), getPluginById);
router.post('/', protect, authorize('admin'), auditLogger('ADMIN_ACTION'), registerPlugin);
router.put('/:id/settings', protect, authorize('admin'), auditLogger('ADMIN_ACTION', 'Plugin'), updatePluginSettings);
router.put('/:id/toggle', protect, authorize('admin'), auditLogger('ADMIN_ACTION', 'Plugin'), togglePluginActive);
router.delete('/:id', protect, authorize('admin'), auditLogger('ADMIN_ACTION', 'Plugin'), deletePlugin);
router.post('/upload', protect, authorize('admin'), auditLogger('ADMIN_ACTION'), uploadPlugin);

// Hook execution - can be used by any authenticated user
router.post('/hook/:hookName', protect, auditLogger('PLUGIN_HOOK'), executeHook);

module.exports = router;