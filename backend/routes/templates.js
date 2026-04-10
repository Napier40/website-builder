const express = require('express');
const router = express.Router();
const {
  getTemplates,
  getTemplateById,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  saveWebsiteAsTemplate,
  getTemplateCategories,
  getTemplateTags
} = require('../controllers/templateController');

const { protect, authorize } = require('../middleware/auth');
const auditLogger = require('../middleware/auditLogger');

// Public routes
router.get('/', getTemplates);
router.get('/categories', getTemplateCategories);
router.get('/tags', getTemplateTags);
router.get('/:id', getTemplateById);

// Protected routes
router.post('/', protect, auditLogger('CREATE', 'Template'), createTemplate);
router.put('/:id', protect, auditLogger('UPDATE', 'Template'), updateTemplate);
router.delete('/:id', protect, auditLogger('DELETE', 'Template'), deleteTemplate);
router.post('/from-website/:websiteId', protect, auditLogger('CREATE', 'Template'), saveWebsiteAsTemplate);

module.exports = router;