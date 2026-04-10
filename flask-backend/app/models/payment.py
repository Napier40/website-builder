"""
Payment Model
Handles payment records and Stripe integration data
"""
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db


class PaymentModel:
    """Payment history model."""

    COLLECTION = 'payments'

    @classmethod
    def get_collection(cls):
        return get_db()[cls.COLLECTION]

    @classmethod
    def create(cls, user_id: str, amount: float, currency: str = 'usd',
               status: str = 'pending', stripe_payment_intent_id: str = None,
               subscription_plan: str = None, description: str = None) -> dict:
        """Record a new payment."""
        now = datetime.now(timezone.utc)
        doc = {
            'user': ObjectId(user_id),
            'amount': amount,
            'currency': currency,
            'status': status,
            'stripePaymentIntentId': stripe_payment_intent_id,
            'subscriptionPlan': subscription_plan,
            'description': description,
            'refunded': False,
            'refundedAt': None,
            'createdAt': now,
            'updatedAt': now
        }
        result = cls.get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return cls.serialize(doc)

    @classmethod
    def find_by_user(cls, user_id: str, skip: int = 0, limit: int = 10) -> tuple[list, int]:
        collection = cls.get_collection()
        query = {'user': ObjectId(user_id)}
        total = collection.count_documents(query)
        cursor = collection.find(query).sort('createdAt', -1).skip(skip).limit(limit)
        return [cls.serialize(doc) for doc in cursor], total

    @classmethod
    def find_by_id(cls, payment_id: str) -> dict | None:
        try:
            doc = cls.get_collection().find_one({'_id': ObjectId(payment_id)})
            return cls.serialize(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def update_status(cls, payment_id: str, status: str) -> dict | None:
        result = cls.get_collection().find_one_and_update(
            {'_id': ObjectId(payment_id)},
            {'$set': {'status': status, 'updatedAt': datetime.now(timezone.utc)}},
            return_document=True
        )
        return cls.serialize(result) if result else None

    @classmethod
    def update_by_stripe_id(cls, stripe_payment_intent_id: str, updates: dict) -> dict | None:
        updates['updatedAt'] = datetime.now(timezone.utc)
        result = cls.get_collection().find_one_and_update(
            {'stripePaymentIntentId': stripe_payment_intent_id},
            {'$set': updates},
            return_document=True
        )
        return cls.serialize(result) if result else None

    @classmethod
    def aggregate_monthly_revenue(cls, days: int = 30) -> float:
        """Calculate total revenue over the last N days."""
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(days=days)
        pipeline = [
            {'$match': {
                'status': 'completed',
                'createdAt': {'$gte': since}
            }},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ]
        result = list(cls.get_collection().aggregate(pipeline))
        return result[0]['total'] if result else 0.0

    @classmethod
    def serialize(cls, doc: dict) -> dict:
        if not doc:
            return doc
        d = dict(doc)
        if '_id' in d and isinstance(d['_id'], ObjectId):
            d['_id'] = str(d['_id'])
        if 'user' in d and isinstance(d['user'], ObjectId):
            d['user'] = str(d['user'])
        for key in ('createdAt', 'updatedAt', 'refundedAt'):
            if key in d and isinstance(d[key], datetime):
                d[key] = d[key].isoformat()
        return d