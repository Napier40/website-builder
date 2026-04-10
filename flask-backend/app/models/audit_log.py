"""
AuditLog Model
Records all significant actions for compliance and debugging
"""
import logging
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db

logger = logging.getLogger(__name__)

VALID_ACTIONS = [
    'LOGIN', 'LOGOUT', 'REGISTER',
    'CREATE', 'READ', 'UPDATE', 'DELETE',
    'PUBLISH', 'UNPUBLISH',
    'SUBSCRIBE', 'UNSUBSCRIBE',
    'PAYMENT', 'REFUND',
    'ADMIN_ACTION', 'MODERATION', 'CONTENT_OVERRIDE',
    'PLUGIN_ACTION', 'TEMPLATE_ACTION'
]


class AuditLogModel:
    """Audit log model for tracking all user and admin actions."""

    COLLECTION = 'audit_logs'

    @classmethod
    def get_collection(cls):
        return get_db()[cls.COLLECTION]

    @classmethod
    def create_log(cls,
                   user_id: str,
                   action: str,
                   resource: str,
                   resource_id: str = None,
                   resource_model: str = None,
                   previous_state: dict = None,
                   new_state: dict = None,
                   details: dict = None,
                   ip_address: str = None,
                   user_agent: str = None) -> dict | None:
        """
        Create an audit log entry. Failures are logged but never raise exceptions
        so they don't interrupt the main application flow.
        """
        try:
            doc = {
                'user': ObjectId(user_id) if user_id else None,
                'action': action if action in VALID_ACTIONS else 'UPDATE',
                'resource': resource,
                'resourceId': ObjectId(resource_id) if resource_id else None,
                'resourceModel': resource_model,
                'previousState': previous_state,
                'newState': new_state,
                'details': details or {},
                'ipAddress': ip_address,
                'userAgent': user_agent,
                'timestamp': datetime.now(timezone.utc)
            }
            result = cls.get_collection().insert_one(doc)
            doc['_id'] = result.inserted_id
            return cls.serialize(doc)
        except Exception as e:
            logger.warning(f"Audit log creation failed (non-critical): {e}")
            return None

    @classmethod
    def find_all(cls, query: dict = None, skip: int = 0, limit: int = 20,
                 sort_field: str = 'timestamp', sort_dir: int = -1) -> tuple[list, int]:
        collection = cls.get_collection()
        query = query or {}
        total = collection.count_documents(query)
        cursor = collection.find(query).sort(sort_field, sort_dir).skip(skip).limit(limit)
        return [cls.serialize(doc) for doc in cursor], total

    @classmethod
    def find_by_user(cls, user_id: str, limit: int = 10) -> list:
        cursor = cls.get_collection() \
            .find({'user': ObjectId(user_id)}) \
            .sort('timestamp', -1) \
            .limit(limit)
        return [cls.serialize(doc) for doc in cursor]

    @classmethod
    def serialize(cls, doc: dict) -> dict:
        if not doc:
            return doc
        d = dict(doc)
        for field in ('_id', 'user', 'resourceId'):
            if field in d and isinstance(d[field], ObjectId):
                d[field] = str(d[field])
        if 'timestamp' in d and isinstance(d['timestamp'], datetime):
            d['timestamp'] = d['timestamp'].isoformat()
        return d