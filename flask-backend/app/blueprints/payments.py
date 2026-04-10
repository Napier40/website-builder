"""
Payments Blueprint
Routes: /api/payments - payment intents, history, Stripe webhooks
"""
import logging
import stripe
from flask import Blueprint, request, jsonify, g, current_app

from app.models.payment import PaymentModel
from app.models.user import UserModel
from app.models.audit_log import AuditLogModel
from app.middleware.auth import jwt_required_custom, authorize
from app.utils.helpers import (
    error_response, paginated_response, get_pagination_params, validate_object_id
)

logger = logging.getLogger(__name__)
payments_bp = Blueprint('payments', __name__)


def get_stripe():
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY', '')
    return stripe


@payments_bp.route('/intent', methods=['POST'])
@jwt_required_custom
def create_payment_intent():
    """
    Create a Stripe PaymentIntent for the frontend to confirm.
    POST /api/payments/intent
    Body: { amount, currency?, description? }
    """
    data = request.get_json() or {}
    amount = data.get('amount')
    if not amount:
        return error_response('amount is required', 400)

    try:
        amount_cents = int(float(amount) * 100)
    except (ValueError, TypeError):
        return error_response('amount must be a valid number', 400)

    currency = data.get('currency', 'usd').lower()
    description = data.get('description', 'Website Builder subscription')

    s = get_stripe()
    try:
        intent = s.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            description=description,
            metadata={'userId': g.user_id}
        )

        # Record pending payment
        payment = PaymentModel.create(
            user_id=g.user_id,
            amount=float(amount),
            currency=currency,
            status='pending',
            stripe_payment_intent_id=intent['id'],
            description=description
        )

        return jsonify({
            'success': True,
            'clientSecret': intent['client_secret'],
            'paymentId': payment['_id'],
            'intentId': intent['id']
        }), 200

    except stripe.error.StripeError as e:
        logger.error(f"Stripe payment intent error: {e}")
        return error_response(f"Payment error: {str(e.user_message)}", 400)
    except Exception as e:
        logger.error(f"Payment intent error: {e}")
        return error_response('Server error creating payment intent', 500)


@payments_bp.route('/history', methods=['GET'])
@jwt_required_custom
def get_payment_history():
    """
    Get the current user's payment history.
    GET /api/payments/history
    """
    page, limit, skip = get_pagination_params()
    payments, total = PaymentModel.find_by_user(g.user_id, skip, limit)
    return paginated_response(payments, total, page, limit)


@payments_bp.route('/<payment_id>', methods=['GET'])
@jwt_required_custom
def get_payment(payment_id):
    """
    Get a specific payment record.
    GET /api/payments/<payment_id>
    """
    if not validate_object_id(payment_id):
        return error_response('Invalid payment ID format', 400)

    payment = PaymentModel.find_by_id(payment_id)
    if not payment:
        return error_response('Payment not found', 404)

    # Only the owner or admin can view a payment
    if payment.get('user') != g.user_id and g.current_user.get('role') != 'admin':
        return error_response('Not authorized to access this payment', 403)

    return jsonify({'success': True, 'payment': payment}), 200


@payments_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events.
    POST /api/payments/webhook
    Stripe sends events here for: payment_intent.succeeded, payment_intent.payment_failed, etc.
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET', '')

    s = get_stripe()

    try:
        if webhook_secret and sig_header:
            event = s.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            # For development/testing without webhook signing
            import json
            event = json.loads(payload)

    except ValueError:
        logger.error("Stripe webhook: invalid payload")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        logger.error("Stripe webhook: invalid signature")
        return jsonify({'error': 'Invalid signature'}), 400

    event_type = event.get('type', '')
    event_data = event.get('data', {}).get('object', {})
    logger.info(f"Stripe webhook received: {event_type}")

    if event_type == 'payment_intent.succeeded':
        payment_intent_id = event_data.get('id')
        PaymentModel.update_by_stripe_id(payment_intent_id, {'status': 'completed'})
        logger.info(f"Payment succeeded: {payment_intent_id}")

    elif event_type == 'payment_intent.payment_failed':
        payment_intent_id = event_data.get('id')
        PaymentModel.update_by_stripe_id(payment_intent_id, {'status': 'failed'})
        logger.info(f"Payment failed: {payment_intent_id}")

    elif event_type == 'customer.subscription.deleted':
        stripe_customer_id = event_data.get('customer')
        if stripe_customer_id:
            # Find user and reset subscription
            from app.database import get_db
            db = get_db()
            db.users.update_one(
                {'stripeCustomerId': stripe_customer_id},
                {'$set': {'subscriptionStatus': 'none', 'subscriptionId': None}}
            )
            logger.info(f"Subscription cancelled for customer: {stripe_customer_id}")

    elif event_type == 'invoice.payment_succeeded':
        logger.info(f"Invoice payment succeeded for: {event_data.get('customer')}")

    return jsonify({'received': True}), 200


@payments_bp.route('/all', methods=['GET'])
@jwt_required_custom
@authorize('admin')
def get_all_payments():
    """
    Admin: get all payments.
    GET /api/payments/all
    """
    from app.database import get_db
    page, limit, skip = get_pagination_params()

    db = get_db()
    total = db.payments.count_documents({})
    cursor = db.payments.find({}).sort('createdAt', -1).skip(skip).limit(limit)

    from app.models.payment import PaymentModel
    payments = [PaymentModel.serialize(doc) for doc in cursor]

    return paginated_response(payments, total, page, limit)