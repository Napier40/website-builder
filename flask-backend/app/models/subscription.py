"""
Subscription Model
Manages subscription plans and user subscription records
"""
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db


class SubscriptionModel:
    """Subscription plan model."""

    COLLECTION = 'subscriptions'

    @classmethod
    def get_collection(cls):
        return get_db()[cls.COLLECTION]

    # ─── Default plans ─────────────────────────────────────────────────────────

    @classmethod
    def seed_default_plans(cls):
        """Insert default subscription plans if they don't exist."""
        plans = [
            {
                'name': 'basic',
                'displayName': 'Basic',
                'price': 9.99,
                'currency': 'usd',
                'interval': 'month',
                'websiteLimit': 3,
                'storageLimit': 1024,  # MB
                'customDomain': False,
                'analyticsEnabled': False,
                'prioritySupport': False,
                'stripePriceId': '',
                'features': [
                    'Up to 3 websites',
                    '1GB storage',
                    'SSL certificate',
                    'Basic templates',
                    'Email support'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc)
            },
            {
                'name': 'premium',
                'displayName': 'Premium',
                'price': 29.99,
                'currency': 'usd',
                'interval': 'month',
                'websiteLimit': 10,
                'storageLimit': 10240,  # MB
                'customDomain': True,
                'analyticsEnabled': True,
                'prioritySupport': False,
                'stripePriceId': '',
                'features': [
                    'Up to 10 websites',
                    '10GB storage',
                    'Custom domains',
                    'Advanced analytics',
                    'Premium templates',
                    'Priority email support'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc)
            },
            {
                'name': 'enterprise',
                'displayName': 'Enterprise',
                'price': 99.99,
                'currency': 'usd',
                'interval': 'month',
                'websiteLimit': 9999,
                'storageLimit': 102400,  # MB
                'customDomain': True,
                'analyticsEnabled': True,
                'prioritySupport': True,
                'stripePriceId': '',
                'features': [
                    'Unlimited websites',
                    '100GB storage',
                    'Custom domains',
                    'Advanced analytics',
                    'All templates',
                    '24/7 priority support',
                    'API access',
                    'White-label options'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc)
            }
        ]

        collection = cls.get_collection()
        for plan in plans:
            if not collection.find_one({'name': plan['name']}):
                collection.insert_one(plan)

    @classmethod
    def find_all_active(cls) -> list:
        """Return all active subscription plans."""
        cursor = cls.get_collection().find({'isActive': True}).sort('price', 1)
        return [cls.serialize(doc) for doc in cursor]

    @classmethod
    def find_by_name(cls, name: str) -> dict | None:
        doc = cls.get_collection().find_one({'name': name})
        return cls.serialize(doc) if doc else None

    @classmethod
    def find_by_id(cls, plan_id: str) -> dict | None:
        try:
            doc = cls.get_collection().find_one({'_id': ObjectId(plan_id)})
            return cls.serialize(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def update_by_id(cls, plan_id: str, updates: dict) -> dict | None:
        result = cls.get_collection().find_one_and_update(
            {'_id': ObjectId(plan_id)},
            {'$set': updates},
            return_document=True
        )
        return cls.serialize(result) if result else None

    @classmethod
    def serialize(cls, doc: dict) -> dict:
        if not doc:
            return doc
        d = dict(doc)
        if '_id' in d and isinstance(d['_id'], ObjectId):
            d['_id'] = str(d['_id'])
        if 'createdAt' in d and isinstance(d['createdAt'], datetime):
            d['createdAt'] = d['createdAt'].isoformat()
        return d