"""
Moderation Model
Tracks content moderation actions by administrators
"""
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db

VALID_STATUSES = ['pending', 'approved', 'rejected', 'under_review']
VALID_ACTIONS = ['no_action', 'content_edited', 'content_removal', 'account_warning', 'account_suspension']


class ModerationModel:
    """Content moderation model."""

    COLLECTION = 'moderation'

    @classmethod
    def get_collection(cls):
        return get_db()[cls.COLLECTION]

    @classmethod
    def create(cls, content_id: str, content_model: str,
               reporter_id: str = None, reason: str = None,
               original_content: dict = None) -> dict:
        """Create a new moderation record."""
        now = datetime.now(timezone.utc)
        doc = {
            'content': ObjectId(content_id),
            'contentModel': content_model,
            'reporter': ObjectId(reporter_id) if reporter_id else None,
            'moderator': None,
            'status': 'pending',
            'reason': reason,
            'action': 'no_action',
            'originalContent': original_content,
            'modifiedContent': None,
            'notes': None,
            'createdAt': now,
            'updatedAt': now
        }
        result = cls.get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return cls.serialize(doc)

    @classmethod
    def find_by_id(cls, mod_id: str) -> dict | None:
        try:
            doc = cls.get_collection().find_one({'_id': ObjectId(mod_id)})
            return cls.serialize(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def find_all(cls, query: dict = None, skip: int = 0, limit: int = 10) -> tuple[list, int]:
        collection = cls.get_collection()
        query = query or {}
        total = collection.count_documents(query)
        cursor = collection.find(query).sort('createdAt', -1).skip(skip).limit(limit)
        return [cls.serialize(doc) for doc in cursor], total

    @classmethod
    def update_by_id(cls, mod_id: str, updates: dict) -> dict | None:
        updates['updatedAt'] = datetime.now(timezone.utc)
        result = cls.get_collection().find_one_and_update(
            {'_id': ObjectId(mod_id)},
            {'$set': updates},
            return_document=True
        )
        return cls.serialize(result) if result else None

    @classmethod
    def aggregate_stats(cls) -> list:
        pipeline = [{'$group': {'_id': '$status', 'count': {'$sum': 1}}}]
        return list(cls.get_collection().aggregate(pipeline))

    @classmethod
    def serialize(cls, doc: dict) -> dict:
        if not doc:
            return doc
        d = dict(doc)
        for field in ('_id', 'content', 'reporter', 'moderator'):
            if field in d and isinstance(d[field], ObjectId):
                d[field] = str(d[field])
        for key in ('createdAt', 'updatedAt'):
            if key in d and isinstance(d[key], datetime):
                d[key] = d[key].isoformat()
        return d