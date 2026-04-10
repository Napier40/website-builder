const Subscription = require('../models/Subscription');
const User = require('../models/User');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// @desc    Get all subscription plans
// @route   GET /api/subscriptions
// @access  Public
exports.getSubscriptions = async (req, res) => {
  try {
    const subscriptions = await Subscription.find({ active: true });
    
    res.status(200).json({
      success: true,
      count: subscriptions.length,
      subscriptions
    });
  } catch (error) {
    console.error('Get subscriptions error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Get subscription by ID
// @route   GET /api/subscriptions/:id
// @access  Public
exports.getSubscriptionById = async (req, res) => {
  try {
    const subscription = await Subscription.findById(req.params.id);
    
    if (!subscription) {
      return res.status(404).json({ success: false, message: 'Subscription not found' });
    }
    
    res.status(200).json({
      success: true,
      subscription
    });
  } catch (error) {
    console.error('Get subscription by ID error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Create subscription plan (admin only)
// @route   POST /api/subscriptions
// @access  Private/Admin
exports.createSubscription = async (req, res) => {
  try {
    const { name, price, features, websiteLimit, storageLimit, customDomain, analytics, ecommerce } = req.body;
    
    // Create product in Stripe
    const product = await stripe.products.create({
      name: `${name.charAt(0).toUpperCase() + name.slice(1)} Plan`,
      description: `${name.charAt(0).toUpperCase() + name.slice(1)} subscription plan`
    });
    
    // Create price in Stripe
    const stripePrice = await stripe.prices.create({
      product: product.id,
      unit_amount: price * 100, // Stripe uses cents
      currency: 'usd',
      recurring: {
        interval: 'month'
      }
    });
    
    // Create subscription in database
    const subscription = await Subscription.create({
      name,
      price,
      features,
      websiteLimit,
      storageLimit,
      customDomain,
      analytics,
      ecommerce,
      stripeProductId: product.id,
      stripePriceId: stripePrice.id
    });
    
    res.status(201).json({
      success: true,
      subscription
    });
  } catch (error) {
    console.error('Create subscription error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Update subscription plan (admin only)
// @route   PUT /api/subscriptions/:id
// @access  Private/Admin
exports.updateSubscription = async (req, res) => {
  try {
    const { name, price, features, websiteLimit, storageLimit, customDomain, analytics, ecommerce, active } = req.body;
    
    // Find subscription
    const subscription = await Subscription.findById(req.params.id);
    
    if (!subscription) {
      return res.status(404).json({ success: false, message: 'Subscription not found' });
    }
    
    // Update fields
    if (name) subscription.name = name;
    if (price) subscription.price = price;
    if (features) subscription.features = features;
    if (websiteLimit) subscription.websiteLimit = websiteLimit;
    if (storageLimit) subscription.storageLimit = storageLimit;
    if (customDomain !== undefined) subscription.customDomain = customDomain;
    if (analytics !== undefined) subscription.analytics = analytics;
    if (ecommerce !== undefined) subscription.ecommerce = ecommerce;
    if (active !== undefined) subscription.active = active;
    
    // Update product in Stripe if name changed
    if (name && subscription.stripeProductId) {
      await stripe.products.update(subscription.stripeProductId, {
        name: `${name.charAt(0).toUpperCase() + name.slice(1)} Plan`
      });
    }
    
    // If price changed, create new price in Stripe
    if (price && subscription.stripeProductId) {
      const stripePrice = await stripe.prices.create({
        product: subscription.stripeProductId,
        unit_amount: price * 100, // Stripe uses cents
        currency: 'usd',
        recurring: {
          interval: 'month'
        }
      });
      
      subscription.stripePriceId = stripePrice.id;
    }
    
    // Save subscription
    await subscription.save();
    
    res.status(200).json({
      success: true,
      subscription
    });
  } catch (error) {
    console.error('Update subscription error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Delete subscription plan (admin only)
// @route   DELETE /api/subscriptions/:id
// @access  Private/Admin
exports.deleteSubscription = async (req, res) => {
  try {
    const subscription = await Subscription.findById(req.params.id);
    
    if (!subscription) {
      return res.status(404).json({ success: false, message: 'Subscription not found' });
    }
    
    // Archive product in Stripe
    if (subscription.stripeProductId) {
      await stripe.products.update(subscription.stripeProductId, {
        active: false
      });
    }
    
    // Set subscription to inactive instead of deleting
    subscription.active = false;
    await subscription.save();
    
    res.status(200).json({
      success: true,
      message: 'Subscription plan deactivated successfully'
    });
  } catch (error) {
    console.error('Delete subscription error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Subscribe user to plan
// @route   POST /api/subscriptions/subscribe
// @access  Private
exports.subscribeUser = async (req, res) => {
  try {
    const { subscriptionId, paymentMethodId } = req.body;
    
    // Find subscription
    const subscription = await Subscription.findById(subscriptionId);
    
    if (!subscription || !subscription.active) {
      return res.status(404).json({ success: false, message: 'Subscription plan not found or inactive' });
    }
    
    // Find user
    const user = await User.findById(req.user._id);
    
    // Create or get Stripe customer
    let customer;
    if (user.stripeCustomerId) {
      customer = await stripe.customers.retrieve(user.stripeCustomerId);
    } else {
      customer = await stripe.customers.create({
        email: user.email,
        name: user.name,
        payment_method: paymentMethodId,
        invoice_settings: {
          default_payment_method: paymentMethodId
        }
      });
      
      user.stripeCustomerId = customer.id;
      await user.save();
    }
    
    // Create subscription in Stripe
    const stripeSubscription = await stripe.subscriptions.create({
      customer: customer.id,
      items: [
        {
          price: subscription.stripePriceId
        }
      ],
      payment_behavior: 'default_incomplete',
      payment_settings: {
        payment_method_types: ['card'],
        save_default_payment_method: 'on_subscription'
      },
      expand: ['latest_invoice.payment_intent']
    });
    
    // Update user subscription status
    user.subscriptionStatus = subscription.name;
    user.subscriptionId = stripeSubscription.id;
    await user.save();
    
    res.status(200).json({
      success: true,
      clientSecret: stripeSubscription.latest_invoice.payment_intent.client_secret,
      subscriptionId: stripeSubscription.id
    });
  } catch (error) {
    console.error('Subscribe user error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Cancel user subscription
// @route   POST /api/subscriptions/cancel
// @access  Private
exports.cancelSubscription = async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    
    if (!user.subscriptionId) {
      return res.status(400).json({ success: false, message: 'No active subscription found' });
    }
    
    // Cancel subscription in Stripe
    await stripe.subscriptions.del(user.subscriptionId);
    
    // Update user subscription status
    user.subscriptionStatus = 'none';
    user.subscriptionId = null;
    await user.save();
    
    res.status(200).json({
      success: true,
      message: 'Subscription cancelled successfully'
    });
  } catch (error) {
    console.error('Cancel subscription error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Get user subscription details
// @route   GET /api/subscriptions/my-subscription
// @access  Private
exports.getMySubscription = async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    
    if (user.subscriptionStatus === 'none' || !user.subscriptionId) {
      return res.status(200).json({
        success: true,
        hasSubscription: false,
        message: 'No active subscription'
      });
    }
    
    // Get subscription details from Stripe
    const stripeSubscription = await stripe.subscriptions.retrieve(user.subscriptionId);
    
    // Get subscription plan details from database
    const subscription = await Subscription.findOne({ name: user.subscriptionStatus });
    
    res.status(200).json({
      success: true,
      hasSubscription: true,
      subscription: {
        id: subscription._id,
        name: subscription.name,
        price: subscription.price,
        features: subscription.features,
        websiteLimit: subscription.websiteLimit,
        storageLimit: subscription.storageLimit,
        customDomain: subscription.customDomain,
        analytics: subscription.analytics,
        ecommerce: subscription.ecommerce
      },
      stripeDetails: {
        status: stripeSubscription.status,
        currentPeriodEnd: new Date(stripeSubscription.current_period_end * 1000),
        cancelAtPeriodEnd: stripeSubscription.cancel_at_period_end
      }
    });
  } catch (error) {
    console.error('Get my subscription error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};