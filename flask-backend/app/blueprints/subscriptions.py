"""
Subscriptions Blueprint
"""
from flask import Blueprint, request, g

from app.models.subscription import Subscription
from app.models.audit_log    import AuditLog
from app.middleware.auth     import jwt_required_custom, authorize
from app.utils.helpers       import success_response, error_response

subscriptions_bp = Blueprint('subscriptions', __name__)


@subscriptions_bp.route('/', methods=['GET'])
def get_plans():
    plans = Subscription.find_all_active()
    return success_response(data={'plans': [p.to_dict() for p in plans]})


@subscriptions_bp.route('/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    plan = Subscription.find_by_id(plan_id)
    if not plan:
        return error_response('Plan not found', 404)
    return success_response(data={'plan': plan.to_dict()})


@subscriptions_bp.route('/current', methods=['GET'])
@jwt_required_custom
def get_current_subscription():
    plan = Subscription.find_by_name(g.current_user.subscription_type)
    return success_response(data={
        'subscriptionType':   g.current_user.subscription_type,
        'subscriptionStatus': g.current_user.subscription_status,
        'plan': plan.to_dict() if plan else None,
    })


@subscriptions_bp.route('/subscribe', methods=['POST'])
@jwt_required_custom
def subscribe():
    data = request.get_json(silent=True) or {}
    plan_name = data.get('plan')
    if not plan_name:
        return error_response('Plan name is required', 400)

    plan = Subscription.find_by_name(plan_name)
    if not plan or not plan.is_active:
        return error_response('Plan not found or inactive', 404)

    g.current_user.update(
        subscription_type=plan.name,
        subscription_status='active',
    )
    AuditLog.create_log(user_id=g.current_user.id, action='SUBSCRIPTION_CHANGE',
                        resource_model='Subscription',
                        description=f'Subscribed to {plan.name}')
    return success_response(
        data={'user': g.current_user.to_dict()},
        message=f'Successfully subscribed to {plan.display_name}',
    )


@subscriptions_bp.route('/cancel', methods=['POST'])
@jwt_required_custom
def cancel_subscription():
    g.current_user.update(
        subscription_type='free',
        subscription_status='cancelled',
    )
    AuditLog.create_log(user_id=g.current_user.id, action='SUBSCRIPTION_CHANGE',
                        resource_model='Subscription',
                        description='Subscription cancelled — reverted to free')
    return success_response(message='Subscription cancelled. You have been moved to the free plan.')


@subscriptions_bp.route('/<int:plan_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_plan(plan_id):
    plan = Subscription.find_by_id(plan_id)
    if not plan:
        return error_response('Plan not found', 404)

    data    = request.get_json(silent=True) or {}
    allowed = {k: v for k, v in data.items()
               if k in ('display_name', 'price', 'currency',
                        'max_websites', 'max_pages', 'features', 'is_active')}
    plan.update(**allowed)
    return success_response(data={'plan': plan.to_dict()}, message='Plan updated')