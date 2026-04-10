const express = require('express');
const router = express.Router();
const {
  getUsers,
  getUserById,
  updateUser,
  deleteUser,
  getModerationQueue,
  processModeration,
  overrideWebsiteContent,
  getAuditLogs,
  getDashboardStats
} = require('../controllers/adminController');

const { protect, authorize } = require('../middleware/auth');
const auditLogger = require('../middleware/auditLogger');

// All routes require admin privileges
router.use(protect);
router.use(authorize('admin'));

// User management routes
router.get('/users', auditLogger('ADMIN_ACTION'), getUsers);
router.get('/users/:id', auditLogger('ADMIN_ACTION'), getUserById);
router.put('/users/:id', auditLogger('ADMIN_ACTION', 'User'), updateUser);
router.delete('/users/:id', auditLogger('ADMIN_ACTION', 'User'), deleteUser);

// Content moderation routes
router.get('/moderation', auditLogger('ADMIN_ACTION'), getModerationQueue);
router.put('/moderation/:id', auditLogger('ADMIN_ACTION', 'Moderation'), processModeration);
router.put('/websites/:id/override', auditLogger('CONTENT_OVERRIDE', 'Website'), overrideWebsiteContent);

// Audit logs routes
router.get('/audit-logs', auditLogger('ADMIN_ACTION'), getAuditLogs);

// Dashboard statistics
router.get('/dashboard', auditLogger('ADMIN_ACTION'), getDashboardStats);

module.exports = router;