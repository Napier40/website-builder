"""
Subscriptions Blueprint
Routes: /api/subscriptions - plan management, subscribe, cancel
"""
import logging
import stripe
from flask import Blueprint, request, jsonify, g, current_app

from app.models.subscription import SubscriptionModel
from app.models.user import UserModel
from app.models.audit_log import AuditLogModel
from app.middleware.auth import jwt_required_custom, authorize
from app.utils.helpers import error_response, validate_object_id

logger = logging.getLogger(__name__)
subscriptions_bp = Blueprint('subscriptions', __name__)


def get_stripe():
    """Initialize stripe with the secret key from app config."""
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY', '')
    return stripe


@subscriptions_bp.route('', methods=['GET'])
def get_plans():
    """
    Get all active subscription plans (public route).
    GET /api/subscriptions
    """
    plans = SubscriptionModel.find_all_active()
    return jsonify({'success': True, 'count': len(plans), 'plans': plans}), 200


@subscriptions_bp.route('/<plan_id>', methods=['GET'])
def get_plan(plan_id):
    """
    Get a specific subscription plan by ID.
    GET /api/subscriptions/<plan_id>
    """
    plan = SubscriptionModel.find_by_id(plan_id)
    if not plan:
        return error_response(f'Subscription plan not found', 404)
    return jsonify({'success': True, 'plan': plan}), 200


@subscriptions_bp.route('/subscribe', methods=['POST'])
@jwt_required_custom
def subscribe():
    """
    Subscribe the current user to a plan via Stripe.
    POST /api/subscriptions/subscribe
    Body: { planName, paymentMethodId }
    """
    data = request.get_json() or {}
    plan_name = data.get('planName')
    payment_method_id = data.get('paymentMethodId')

    if not plan_name:
        return error_response('planName is required', 400)

    plan = SubscriptionModel.find_by_name(plan_name)
    if not plan:
        return error_response(f"Subscription plan '{plan_name}' not found", 404)

    user = g.current_user
    s = get_stripe()

    try:
        # Create or retrieve Stripe customer
        stripe_customer_id = user.get('stripeCustomerId')

        if not stripe_customer_id:
            customer = s.Customer.create(
                email=user.get('email'),
                name=user.get('name'),
                metadata={'userId': str(user['_id'])}
            )
            stripe_customer_id = customer['id']
            UserModel.update_by_id(g.user_id, {'stripeCustomerId': stripe_customer_id})

        # Attach payment method to customer
        if payment_method_id:
            s.PaymentMethod.attach(payment_method_id, customer=stripe_customer_id)
            s.Customer.modify(
                stripe_customer_id,
                invoice_settings={'default_payment_method': payment_method_id}
            )

        # Create Stripe subscription
        stripe_price_id = plan.get('stripePriceId')
        subscription_params = {
            'customer': stripe_customer_id,
            'metadata': {
                'userId': str(user['_id']),
                'planName': plan_name
            }
        }

        if stripe_price_id:
            subscription_params['items'] = [{'price': stripe_price_id}]
        else:
            # Fallback: create a price on-the-fly for testing
            subscription_params['items'] = [{
                'price_data': {
                    'currency': plan.get('currency', 'usd'),
                    'unit_amount': int(plan.get('price', 0) * 100),
                    'recurring': {'interval': plan.get('interval', 'month')},
                    'product_data': {'name': plan.get('displayName', plan_name)}
                }
            }]

        stripe_sub = s.Subscription.create(**subscription_params)

        # Update user's subscription status
        UserModel.update_by_id(g.user_id, {
            'subscriptionStatus': plan_name,
            'subscriptionId': stripe_sub['id'],
            'stripeCustomerId': stripe_customer_id
        })

        # Audit log
        AuditLogModel.create_log(
            user_id=g.user_id, action='SUBSCRIBE',
            resource='/api/subscriptions/subscribe',
            details={'planName': plan_name, 'stripeSubscriptionId': stripe_sub['id']}
        )

        return jsonify({
            'success': True,
            'message': f"Successfully subscribed to {plan.get('displayName')} plan",
            'subscription': {
                'id': stripe_sub['id'],
                'status': stripe_sub['status'],
                'planName': plan_name
            }
        }), 200

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during subscribe: {e}")
        return error_response(f"Payment error: {str(e.user_message)}", 400)
    except Exception as e:
        logger.error(f"Subscribe error: {e}")
        return error_response('Server error processing subscription', 500)


@subscriptions_bp.route('/cancel', methods=['POST'])
@jwt_required_custom
def cancel_subscription():
    """
    Cancel the current user's active Stripe subscription.
    POST /api/subscriptions/cancel
    """
    user = g.current_user
    subscription_id = user.get('subscriptionId')

    if not subscription_id:
        return error_response('You do not have an active subscription to cancel', 400)

    s = get_stripe()

    try:
        s.Subscription.cancel(subscription_id)

        UserModel.update_by_id(g.user_id, {
            'subscriptionStatus': 'none',
            'subscriptionId': None
        })

        AuditLogModel.create_log(
            user_id=g.user_id, action='UNSUBSCRIBE',
            resource='/api/subscriptions/cancel',
            details={'cancelledSubscriptionId': subscription_id}
        )

        return jsonify({
            'success': True,
            'message': 'Subscription cancelled successfully'
        }), 200

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during cancellation: {e}")
        return error_response(f"Payment error: {str(e.user_message)}", 400)
    except Exception as e:
        logger.error(f"Cancel subscription error: {e}")
        return error_response('Server error cancelling subscription', 500)


@subscriptions_bp.route('/current', methods=['GET'])
@jwt_required_custom
def get_current_subscription():
    """
    Get the current user's subscription details.
    GET /api/subscriptions/current
    """
    user = g.current_user
    plan_name = user.get('subscriptionStatus', 'none')

    if plan_name == 'none':
        return jsonify({
            'success': True,
            'subscription': None,
            'plan': None
        }), 200

    plan = SubscriptionModel.find_by_name(plan_name)
    return jsonify({
        'success': True,
        'subscription': {
            'status': plan_name,
            'subscriptionId': user.get('subscriptionId')
        },
        'plan': plan
    }), 200


# ─── Admin plan management ────────────────────────────────────────────────────

@subscriptions_bp.route('/<plan_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_plan(plan_id):
    """
    Admin: update a subscription plan.
    PUT /api/subscriptions/<plan_id>
    """
    if not validate_object_id(plan_id):
        return error_response('Invalid plan ID format', 400)

    data = request.get_json() or {}
    allowed = ['displayName', 'description', 'price', 'websiteLimit',
               'storageLimit', 'customDomain', 'analyticsEnabled',
               'prioritySupport', 'features', 'isActive', 'stripePriceId']
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return error_response('No valid fields to update', 400)

    plan = SubscriptionModel.update_by_id(plan_id, updates)
    if not plan:
        return error_response('Subscription plan not found', 404)

    return jsonify({'success': True, 'plan': plan}), 200