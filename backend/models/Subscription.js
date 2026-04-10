const mongoose = require('mongoose');

const SubscriptionSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    enum: ['basic', 'premium', 'enterprise']
  },
  price: {
    type: Number,
    required: true
  },
  currency: {
    type: String,
    default: 'usd'
  },
  features: [{
    type: String
  }],
  websiteLimit: {
    type: Number,
    required: true
  },
  storageLimit: {
    type: Number,  // in MB
    required: true
  },
  customDomain: {
    type: Boolean,
    default: false
  },
  analytics: {
    type: Boolean,
    default: false
  },
  ecommerce: {
    type: Boolean,
    default: false
  },
  stripeProductId: {
    type: String
  },
  stripePriceId: {
    type: String
  },
  active: {
    type: Boolean,
    default: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Subscription', SubscriptionSchema);