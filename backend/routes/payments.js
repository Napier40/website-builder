const express = require('express');
const router = express.Router();
const { 
  createPaymentIntent, 
  getPaymentMethods, 
  addPaymentMethod, 
  deletePaymentMethod,
  getPaymentHistory,
  handleWebhook
} = require('../controllers/paymentController');
const { protect } = require('../middleware/auth');

// Webhook route (public)
router.post('/webhook', express.raw({ type: 'application/json' }), handleWebhook);

// Protected routes
router.use(protect);
router.post('/create-payment-intent', createPaymentIntent);
router.get('/payment-methods', getPaymentMethods);
router.post('/payment-methods', addPaymentMethod);
router.delete('/payment-methods/:id', deletePaymentMethod);
router.get('/history', getPaymentHistory);

module.exports = router;