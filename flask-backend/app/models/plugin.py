"""
Plugin Model
Registry for installed plugins and their configuration
"""
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db


class PluginModel:
    """Plugin registry model."""

    COLLECTION = 'plugins'

    @classmethod
    def get_collection(cls):
        return get_db()[cls.COLLECTION]

    @classmethod
    def create(cls, name: str, display_name: str, description: str,
               version: str, author: str, entry_point: str,
               hooks: list = None, settings: dict = None) -> dict:
        """Register a new plugin."""
        collection = cls.get_collection()
        if collection.find_one({'name': name}):
            raise ValueError(f"Plugin '{name}' is already registered")

        now = datetime.now(timezone.utc)
        doc = {
            'name': name,
            'displayName': display_name,
            'description': description,
            'version': version,
            'author': author,
            'entryPoint': entry_point,
            'hooks': hooks or [],
            'settings': settings or {},
            'isActive': False,
            'installedAt': now,
            'updatedAt': now
        }
        result = collection.insert_one(doc)
        doc['_id'] = result.inserted_id
        return cls.serialize(doc)

    @classmethod
    def find_all(cls, query: dict = None) -> list:
        cursor = cls.get_collection().find(query or {}).sort('name', 1)
        return [cls.serialize(doc) for doc in cursor]

    @classmethod
    def find_by_id(cls, plugin_id: str) -> dict | None:
        try:
            doc = cls.get_collection().find_one({'_id': ObjectId(plugin_id)})
            return cls.serialize(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def find_by_name(cls, name: str) -> dict | None:
        doc = cls.get_collection().find_one({'name': name})
        return cls.serialize(doc) if doc else None

    @classmethod
    def update_by_id(cls, plugin_id: str, updates: dict) -> dict | None:
        updates['updatedAt'] = datetime.now(timezone.utc)
        result = cls.get_collection().find_one_and_update(
            {'_id': ObjectId(plugin_id)},
            {'$set': updates},
            return_document=True
        )
        return cls.serialize(result) if result else None

    @classmethod
    def toggle_active(cls, plugin_id: str) -> dict | None:
        """Toggle the isActive flag on a plugin."""
        doc = cls.get_collection().find_one({'_id': ObjectId(plugin_id)})
        if not doc:
            return None
        new_state = not doc.get('isActive', False)
        return cls.update_by_id(plugin_id, {'isActive': new_state})

    @classmethod
    def delete_by_id(cls, plugin_id: str) -> bool:
        result = cls.get_collection().delete_one({'_id': ObjectId(plugin_id)})
        return result.deleted_count > 0

    @classmethod
    def serialize(cls, doc: dict) -> dict:
        if not doc:
            return doc
        d = dict(doc)
        if '_id' in d and isinstance(d['_id'], ObjectId):
            d['_id'] = str(d['_id'])
        for key in ('installedAt', 'updatedAt'):
            if key in d and isinstance(d[key], datetime):
                d[key] = d[key].isoformat()
        return d