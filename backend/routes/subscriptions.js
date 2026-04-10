const express = require('express');
const router = express.Router();
const { 
  getSubscriptions, 
  getSubscriptionById, 
  createSubscription, 
  updateSubscription, 
  deleteSubscription,
  subscribeUser,
  cancelSubscription,
  getMySubscription
} = require('../controllers/subscriptionController');
const { protect, authorize } = require('../middleware/auth');

// Public routes
router.get('/', getSubscriptions);
router.get('/:id', getSubscriptionById);

// Protected routes
router.use(protect);
router.post('/subscribe', subscribeUser);
router.post('/cancel', cancelSubscription);
router.get('/my-subscription', getMySubscription);

// Admin only routes
router.post('/', protect, authorize('admin'), createSubscription);
router.put('/:id', protect, authorize('admin'), updateSubscription);
router.delete('/:id', protect, authorize('admin'), deleteSubscription);

module.exports = router;