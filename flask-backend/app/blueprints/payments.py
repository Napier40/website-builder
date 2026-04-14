"""
Payments Blueprint — Stripe integration
"""
import logging
from flask import Blueprint, request, g

from app.models.payment   import Payment
from app.models.audit_log import AuditLog
from app.middleware.auth  import jwt_required_custom, authorize
from app.utils.helpers    import (success_response, error_response,
                                   paginated_response, get_pagination_params)

logger = logging.getLogger(__name__)
payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/intent', methods=['POST'])
@jwt_required_custom
def create_payment_intent():
    """Create a Stripe PaymentIntent and record the pending payment."""
    import stripe
    from flask import current_app
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY', '')

    data = request.get_json(silent=True) or {}
    amount = data.get('amount')
    if not amount or not isinstance(amount, (int, float)) or amount <= 0:
        return error_response('A valid amount (> 0) is required', 400)

    currency          = data.get('currency', 'usd').lower()
    subscription_type = data.get('subscriptionType')

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),   # Stripe expects cents
            currency=currency,
            metadata={
                'user_id':           str(g.current_user.id),
                'subscription_type': subscription_type or '',
            },
        )

        payment = Payment.create(
            user_id=g.current_user.id,
            amount=amount,
            currency=currency,
            status='pending',
            stripe_payment_intent_id=intent.id,
            subscription_type=subscription_type,
            description=data.get('description'),
        )

        AuditLog.create_log(user_id=g.current_user.id, action='PAYMENT',
                            resource_model='Payment', resource_id=payment.id,
                            description=f'Payment intent created: {intent.id}')

        return success_response(
            data={
                'clientSecret': intent.client_secret,
                'paymentId':    payment.id,
            },
            message='Payment intent created',
            status_code=201,
        )

    except Exception as e:
        logger.error(f"Stripe error: {e}")
        return error_response(f'Payment processing error: {str(e)}', 500)


@payments_bp.route('/history', methods=['GET'])
@jwt_required_custom
def get_payment_history():
    page, limit, _ = get_pagination_params()
    items, total   = Payment.find_by_user(g.current_user.id, page=page, limit=limit)
    return paginated_response([p.to_dict() for p in items], total, page, limit)


@payments_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required_custom
def get_payment(payment_id):
    payment = Payment.find_by_id(payment_id)
    if not payment:
        return error_response('Payment not found', 404)
    if payment.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)
    return success_response(data={'payment': payment.to_dict()})


@payments_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    import stripe
    from flask import current_app
    stripe.api_key            = current_app.config.get('STRIPE_SECRET_KEY', '')
    webhook_secret            = current_app.config.get('STRIPE_WEBHOOK_SECRET', '')
    payload                   = request.get_data()
    sig_header                = request.headers.get('Stripe-Signature', '')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        return error_response('Invalid webhook signature', 400)
    except Exception as e:
        return error_response(f'Webhook error: {e}', 400)

    if event['type'] == 'payment_intent.succeeded':
        pi      = event['data']['object']
        payment = Payment.find_by_stripe_id(pi['id'])
        if payment:
            payment.update_status('succeeded')
            # Upgrade subscription if applicable
            user_id           = pi.get('metadata', {}).get('user_id')
            subscription_type = pi.get('metadata', {}).get('subscription_type')
            if user_id and subscription_type:
                from app.models.user import User
                user = User.find_by_id(user_id)
                if user:
                    user.update(subscription_type=subscription_type,
                                subscription_status='active')

    elif event['type'] == 'payment_intent.payment_failed':
        pi      = event['data']['object']
        payment = Payment.find_by_stripe_id(pi['id'])
        if payment:
            payment.update_status('failed')

    return success_response(message='Webhook received')


@payments_bp.route('/all', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_all_payments():
    page, limit, _ = get_pagination_params()
    items, total   = Payment.find_all(page=page, limit=limit)
    return paginated_response([p.to_dict() for p in items], total, page, limit)


@payments_bp.route('/payment-methods', methods=['GET'])
@jwt_required_custom
def get_payment_methods():
    """List Stripe payment methods saved for the current user."""
    import stripe
    from flask import current_app
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY', '')

    user = g.current_user

    # If no Stripe customer yet, return empty list
    if not user.stripe_customer_id:
        return success_response(data={'paymentMethods': []})

    try:
        methods = stripe.PaymentMethod.list(
            customer=user.stripe_customer_id,
            type='card',
        )
        payment_methods = [
            {
                'id':    pm.id,
                'brand': pm.card.brand,
                'last4': pm.card.last4,
                'expMonth': pm.card.exp_month,
                'expYear':  pm.card.exp_year,
            }
            for pm in methods.data
        ]
        return success_response(data={'paymentMethods': payment_methods})
    except Exception as e:
        logger.error(f"Stripe error fetching payment methods: {e}")
        return success_response(data={'paymentMethods': []})


@payments_bp.route('/payment-methods/<string:payment_method_id>', methods=['DELETE'])
@jwt_required_custom
def delete_payment_method(payment_method_id):
    """Detach a saved Stripe payment method from the current user."""
    import stripe
    from flask import current_app
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY', '')

    try:
        stripe.PaymentMethod.detach(payment_method_id)
        return success_response(message='Payment method removed')
    except Exception as e:
        logger.error(f"Stripe error detaching payment method: {e}")
        return error_response(f'Could not remove payment method: {str(e)}', 500)