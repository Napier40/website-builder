const express = require('express');
const router = express.Router();
const { 
  getMyWebsites, 
  getWebsiteById, 
  createWebsite, 
  updateWebsite, 
  deleteWebsite,
  createPage,
  updatePage,
  deletePage,
  publishWebsite,
  unpublishWebsite
} = require('../controllers/websiteController');
const { protect } = require('../middleware/auth');

// All routes are protected
router.use(protect);

// Website routes
router.get('/', getMyWebsites);
router.post('/', createWebsite);
router.get('/:id', getWebsiteById);
router.put('/:id', updateWebsite);
router.delete('/:id', deleteWebsite);
router.put('/:id/publish', publishWebsite);
router.put('/:id/unpublish', unpublishWebsite);

// Page routes
router.post('/:id/pages', createPage);
router.put('/:id/pages/:pageId', updatePage);
router.delete('/:id/pages/:pageId', deletePage);

module.exports = router;