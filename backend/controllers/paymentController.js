const Payment = require('../models/Payment');
const User = require('../models/User');
const Subscription = require('../models/Subscription');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// @desc    Create payment intent
// @route   POST /api/payments/create-payment-intent
// @access  Private
exports.createPaymentIntent = async (req, res) => {
  try {
    const { subscriptionId } = req.body;
    
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
        name: user.name
      });
      
      user.stripeCustomerId = customer.id;
      await user.save();
    }
    
    // Create payment intent
    const paymentIntent = await stripe.paymentIntents.create({
      amount: subscription.price * 100, // Stripe uses cents
      currency: 'usd',
      customer: customer.id,
      metadata: {
        userId: user._id.toString(),
        subscriptionId: subscription._id.toString(),
        subscriptionName: subscription.name
      }
    });
    
    res.status(200).json({
      success: true,
      clientSecret: paymentIntent.client_secret
    });
  } catch (error) {
    console.error('Create payment intent error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Get payment methods
// @route   GET /api/payments/payment-methods
// @access  Private
exports.getPaymentMethods = async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    
    if (!user.stripeCustomerId) {
      return res.status(200).json({
        success: true,
        paymentMethods: []
      });
    }
    
    // Get payment methods from Stripe
    const paymentMethods = await stripe.paymentMethods.list({
      customer: user.stripeCustomerId,
      type: 'card'
    });
    
    res.status(200).json({
      success: true,
      paymentMethods: paymentMethods.data
    });
  } catch (error) {
    console.error('Get payment methods error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Add payment method
// @route   POST /api/payments/payment-methods
// @access  Private
exports.addPaymentMethod = async (req, res) => {
  try {
    const { paymentMethodId } = req.body;
    
    const user = await User.findById(req.user._id);
    
    // Create or get Stripe customer
    let customer;
    if (user.stripeCustomerId) {
      customer = await stripe.customers.retrieve(user.stripeCustomerId);
    } else {
      customer = await stripe.customers.create({
        email: user.email,
        name: user.name
      });
      
      user.stripeCustomerId = customer.id;
      await user.save();
    }
    
    // Attach payment method to customer
    await stripe.paymentMethods.attach(paymentMethodId, {
      customer: user.stripeCustomerId
    });
    
    // Set as default payment method
    await stripe.customers.update(user.stripeCustomerId, {
      invoice_settings: {
        default_payment_method: paymentMethodId
      }
    });
    
    res.status(200).json({
      success: true,
      message: 'Payment method added successfully'
    });
  } catch (error) {
    console.error('Add payment method error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Delete payment method
// @route   DELETE /api/payments/payment-methods/:id
// @access  Private
exports.deletePaymentMethod = async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    
    if (!user.stripeCustomerId) {
      return res.status(404).json({ success: false, message: 'No payment methods found' });
    }
    
    // Detach payment method from customer
    await stripe.paymentMethods.detach(req.params.id);
    
    res.status(200).json({
      success: true,
      message: 'Payment method deleted successfully'
    });
  } catch (error) {
    console.error('Delete payment method error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Get payment history
// @route   GET /api/payments/history
// @access  Private
exports.getPaymentHistory = async (req, res) => {
  try {
    const payments = await Payment.find({ user: req.user._id })
      .sort({ createdAt: -1 })
      .populate('subscription', 'name price');
    
    res.status(200).json({
      success: true,
      count: payments.length,
      payments
    });
  } catch (error) {
    console.error('Get payment history error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Webhook handler for Stripe events
// @route   POST /api/payments/webhook
// @access  Public
exports.handleWebhook = async (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;
  
  try {
    event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error(`Webhook Error: ${err.message}`);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
  
  // Handle the event
  switch (event.type) {
    case 'payment_intent.succeeded':
      const paymentIntent = event.data.object;
      await handlePaymentIntentSucceeded(paymentIntent);
      break;
    case 'invoice.payment_succeeded':
      const invoice = event.data.object;
      await handleInvoicePaymentSucceeded(invoice);
      break;
    case 'customer.subscription.updated':
      const subscription = event.data.object;
      await handleSubscriptionUpdated(subscription);
      break;
    case 'customer.subscription.deleted':
      const cancelledSubscription = event.data.object;
      await handleSubscriptionCancelled(cancelledSubscription);
      break;
    default:
      console.log(`Unhandled event type ${event.type}`);
  }
  
  // Return a 200 response to acknowledge receipt of the event
  res.status(200).json({ received: true });
};

// Helper function to handle payment intent succeeded
async function handlePaymentIntentSucceeded(paymentIntent) {
  try {
    const { userId, subscriptionId } = paymentIntent.metadata;
    
    if (!userId || !subscriptionId) {
      console.error('Missing metadata in payment intent');
      return;
    }
    
    // Find user and subscription
    const user = await User.findById(userId);
    const subscription = await Subscription.findById(subscriptionId);
    
    if (!user || !subscription) {
      console.error('User or subscription not found');
      return;
    }
    
    // Create payment record
    await Payment.create({
      user: userId,
      subscription: subscriptionId,
      amount: paymentIntent.amount / 100, // Convert from cents
      currency: paymentIntent.currency,
      status: 'completed',
      paymentMethod: 'card',
      stripePaymentId: paymentIntent.id
    });
    
  } catch (error) {
    console.error('Error handling payment intent succeeded:', error);
  }
}

// Helper function to handle invoice payment succeeded
async function handleInvoicePaymentSucceeded(invoice) {
  try {
    const customerId = invoice.customer;
    const subscriptionId = invoice.subscription;
    
    // Find user by Stripe customer ID
    const user = await User.findOne({ stripeCustomerId: customerId });
    
    if (!user) {
      console.error('User not found for customer:', customerId);
      return;
    }
    
    // Get subscription details from Stripe
    const stripeSubscription = await stripe.subscriptions.retrieve(subscriptionId);
    
    // Find subscription plan by Stripe price ID
    const stripePriceId = stripeSubscription.items.data[0].price.id;
    const subscription = await Subscription.findOne({ stripePriceId });
    
    if (!subscription) {
      console.error('Subscription not found for price:', stripePriceId);
      return;
    }
    
    // Create payment record
    await Payment.create({
      user: user._id,
      subscription: subscription._id,
      amount: invoice.amount_paid / 100, // Convert from cents
      currency: invoice.currency,
      status: 'completed',
      paymentMethod: 'card',
      stripeInvoiceId: invoice.id,
      billingPeriodStart: new Date(stripeSubscription.current_period_start * 1000),
      billingPeriodEnd: new Date(stripeSubscription.current_period_end * 1000)
    });
    
    // Update user subscription status if needed
    if (user.subscriptionStatus !== subscription.name) {
      user.subscriptionStatus = subscription.name;
      await user.save();
    }
    
  } catch (error) {
    console.error('Error handling invoice payment succeeded:', error);
  }
}

// Helper function to handle subscription updated
async function handleSubscriptionUpdated(subscription) {
  try {
    const customerId = subscription.customer;
    
    // Find user by Stripe customer ID
    const user = await User.findOne({ stripeCustomerId: customerId });
    
    if (!user) {
      console.error('User not found for customer:', customerId);
      return;
    }
    
    // Update user subscription ID
    user.subscriptionId = subscription.id;
    
    // If subscription is active, update subscription status
    if (subscription.status === 'active') {
      // Get price ID from subscription
      const stripePriceId = subscription.items.data[0].price.id;
      
      // Find subscription plan by Stripe price ID
      const subscriptionPlan = await Subscription.findOne({ stripePriceId });
      
      if (subscriptionPlan) {
        user.subscriptionStatus = subscriptionPlan.name;
      }
    }
    
    await user.save();
    
  } catch (error) {
    console.error('Error handling subscription updated:', error);
  }
}

// Helper function to handle subscription cancelled
async function handleSubscriptionCancelled(subscription) {
  try {
    const customerId = subscription.customer;
    
    // Find user by Stripe customer ID
    const user = await User.findOne({ stripeCustomerId: customerId });
    
    if (!user) {
      console.error('User not found for customer:', customerId);
      return;
    }
    
    // Update user subscription status
    user.subscriptionStatus = 'none';
    user.subscriptionId = null;
    
    await user.save();
    
  } catch (error) {
    console.error('Error handling subscription cancelled:', error);
  }
}