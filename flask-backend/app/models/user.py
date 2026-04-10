"""
User Model
Handles all user-related database operations using PyMongo
"""
import bcrypt
import logging
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db

logger = logging.getLogger(__name__)

VALID_ROLES = ['user', 'admin']
VALID_SUBSCRIPTION_STATUSES = ['none', 'basic', 'premium', 'enterprise']


class UserModel:
    """User model providing CRUD operations and business logic."""

    COLLECTION = 'users'

    @classmethod
    def get_collection(cls):
        """Get the users collection from the current database."""
        return get_db()[cls.COLLECTION]

    # ─── Create ────────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, name: str, email: str, password: str, role: str = 'user') -> dict:
        """
        Create a new user with a hashed password.
        Returns the created user document (without password).
        """
        collection = cls.get_collection()

        # Check for duplicate email
        if collection.find_one({'email': email.lower().strip()}):
            raise ValueError('User with this email already exists')

        # Validate role
        if role not in VALID_ROLES:
            role = 'user'

        # Hash password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))

        now = datetime.now(timezone.utc)
        user_doc = {
            'name': name.strip(),
            'email': email.lower().strip(),
            'password': hashed_pw.decode('utf-8'),
            'role': role,
            'subscriptionStatus': 'none',
            'subscriptionId': None,
            'stripeCustomerId': None,
            'isActive': True,
            'createdAt': now,
            'updatedAt': now
        }

        result = collection.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return cls.sanitize(user_doc)

    # ─── Read ──────────────────────────────────────────────────────────────────

    @classmethod
    def find_by_id(cls, user_id: str, include_password: bool = False) -> dict | None:
        """Find a user by their MongoDB ObjectId string."""
        try:
            doc = cls.get_collection().find_one({'_id': ObjectId(user_id)})
            if doc:
                return doc if include_password else cls.sanitize(doc)
            return None
        except Exception:
            return None

    @classmethod
    def find_by_email(cls, email: str, include_password: bool = True) -> dict | None:
        """Find a user by email address."""
        doc = cls.get_collection().find_one({'email': email.lower().strip()})
        if doc:
            return doc if include_password else cls.sanitize(doc)
        return None

    @classmethod
    def find_all(cls, query: dict = None, skip: int = 0, limit: int = 10,
                 sort_field: str = 'createdAt', sort_dir: int = -1) -> tuple[list, int]:
        """
        Find all users matching query with pagination.
        Returns (users_list, total_count).
        """
        collection = cls.get_collection()
        query = query or {}

        total = collection.count_documents(query)
        cursor = collection.find(query, {'password': 0}) \
            .sort(sort_field, sort_dir) \
            .skip(skip) \
            .limit(limit)

        users = [cls.serialize(doc) for doc in cursor]
        return users, total

    # ─── Update ────────────────────────────────────────────────────────────────

    @classmethod
    def update_by_id(cls, user_id: str, updates: dict) -> dict | None:
        """Update a user by ID. Returns the updated user document."""
        collection = cls.get_collection()
        updates['updatedAt'] = datetime.now(timezone.utc)

        # Never allow direct password update through this method
        updates.pop('password', None)

        result = collection.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': updates},
            return_document=True
        )
        return cls.sanitize(result) if result else None

    @classmethod
    def update_password(cls, user_id: str, new_password: str) -> bool:
        """Hash and update a user's password."""
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(10))
        result = cls.get_collection().update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'password': hashed.decode('utf-8'),
                'updatedAt': datetime.now(timezone.utc)
            }}
        )
        return result.modified_count > 0

    # ─── Delete ────────────────────────────────────────────────────────────────

    @classmethod
    def delete_by_id(cls, user_id: str) -> bool:
        """Delete a user by ID. Returns True if deleted."""
        result = cls.get_collection().delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0

    # ─── Auth helpers ──────────────────────────────────────────────────────────

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Compare a plain text password against a bcrypt hash."""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    @classmethod
    def count(cls, query: dict = None) -> int:
        """Count documents matching query."""
        return cls.get_collection().count_documents(query or {})

    # ─── Aggregation ──────────────────────────────────────────────────────────

    @classmethod
    def aggregate_subscription_stats(cls) -> list:
        """Group users by subscriptionStatus and return counts."""
        pipeline = [
            {'$group': {'_id': '$subscriptionStatus', 'count': {'$sum': 1}}}
        ]
        return list(cls.get_collection().aggregate(pipeline))

    # ─── Serialization ────────────────────────────────────────────────────────

    @classmethod
    def sanitize(cls, doc: dict) -> dict:
        """Remove sensitive fields (password) and serialize ObjectIds."""
        if not doc:
            return doc
        d = dict(doc)
        d.pop('password', None)
        return cls.serialize(d)

    @classmethod
    def serialize(cls, doc: dict) -> dict:
        """Convert ObjectId and datetime fields to JSON-serializable types."""
        if not doc:
            return doc
        d = dict(doc)
        if '_id' in d and isinstance(d['_id'], ObjectId):
            d['_id'] = str(d['_id'])
        for key in ('createdAt', 'updatedAt'):
            if key in d and isinstance(d[key], datetime):
                d[key] = d[key].isoformat()
        return d