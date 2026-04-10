"""
Template Model
Website templates that users can apply to their sites
"""
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db


class TemplateModel:
    """Website template model."""

    COLLECTION = 'templates'

    VALID_CATEGORIES = [
        'business', 'portfolio', 'blog', 'ecommerce',
        'landing', 'personal', 'nonprofit', 'education', 'other'
    ]

    @classmethod
    def get_collection(cls):
        return get_db()[cls.COLLECTION]

    @classmethod
    def create(cls, name: str, display_name: str, description: str,
               category: str, thumbnail: str = None, preview_url: str = None,
               content: dict = None, settings: dict = None, tags: list = None,
               is_premium: bool = False, is_public: bool = True,
               created_by: str = None) -> dict:
        """Create a new template."""
        now = datetime.now(timezone.utc)
        doc = {
            'name': name,
            'displayName': display_name,
            'description': description,
            'category': category if category in cls.VALID_CATEGORIES else 'other',
            'thumbnail': thumbnail,
            'previewUrl': preview_url,
            'content': content or {},
            'settings': settings or {},
            'tags': tags or [],
            'isPremium': is_premium,
            'isPublic': is_public,
            'usageCount': 0,
            'rating': 0.0,
            'createdBy': ObjectId(created_by) if created_by else None,
            'createdAt': now,
            'updatedAt': now
        }
        result = cls.get_collection().insert_one(doc)
        doc['_id'] = result.inserted_id
        return cls.serialize(doc)

    @classmethod
    def find_all(cls, query: dict = None, skip: int = 0,
                 limit: int = 10, sort_field: str = 'usageCount',
                 sort_dir: int = -1) -> tuple[list, int]:
        collection = cls.get_collection()
        query = query or {}
        total = collection.count_documents(query)
        cursor = collection.find(query).sort(sort_field, sort_dir).skip(skip).limit(limit)
        return [cls.serialize(doc) for doc in cursor], total

    @classmethod
    def find_by_id(cls, template_id: str) -> dict | None:
        try:
            doc = cls.get_collection().find_one({'_id': ObjectId(template_id)})
            return cls.serialize(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def find_public(cls, category: str = None, is_premium: bool = None,
                    skip: int = 0, limit: int = 10) -> tuple[list, int]:
        query = {'isPublic': True}
        if category:
            query['category'] = category
        if is_premium is not None:
            query['isPremium'] = is_premium
        return cls.find_all(query, skip, limit)

    @classmethod
    def get_categories(cls) -> list:
        """Return all distinct categories in use."""
        return cls.get_collection().distinct('category', {'isPublic': True})

    @classmethod
    def get_tags(cls) -> list:
        """Return all distinct tags in use."""
        return cls.get_collection().distinct('tags', {'isPublic': True})

    @classmethod
    def update_by_id(cls, template_id: str, updates: dict) -> dict | None:
        updates['updatedAt'] = datetime.now(timezone.utc)
        result = cls.get_collection().find_one_and_update(
            {'_id': ObjectId(template_id)},
            {'$set': updates},
            return_document=True
        )
        return cls.serialize(result) if result else None

    @classmethod
    def increment_usage(cls, template_id: str):
        cls.get_collection().update_one(
            {'_id': ObjectId(template_id)},
            {'$inc': {'usageCount': 1}}
        )

    @classmethod
    def delete_by_id(cls, template_id: str) -> bool:
        result = cls.get_collection().delete_one({'_id': ObjectId(template_id)})
        return result.deleted_count > 0

    @classmethod
    def seed_default_templates(cls):
        """Seed default templates if none exist."""
        if cls.get_collection().count_documents({}) > 0:
            return
        defaults = [
            {
                'name': 'default', 'displayName': 'Clean Business',
                'description': 'A clean, professional business template',
                'category': 'business', 'tags': ['clean', 'professional'],
                'isPremium': False, 'isPublic': True
            },
            {
                'name': 'portfolio', 'displayName': 'Creative Portfolio',
                'description': 'Showcase your work with this modern portfolio',
                'category': 'portfolio', 'tags': ['creative', 'modern'],
                'isPremium': False, 'isPublic': True
            },
            {
                'name': 'blog', 'displayName': 'Minimal Blog',
                'description': 'Perfect for writers and content creators',
                'category': 'blog', 'tags': ['minimal', 'clean'],
                'isPremium': False, 'isPublic': True
            },
            {
                'name': 'landing', 'displayName': 'Product Launch',
                'description': 'High-converting landing page template',
                'category': 'landing', 'tags': ['conversion', 'marketing'],
                'isPremium': True, 'isPublic': True
            }
        ]
        for t in defaults:
            cls.create(**t)

    @classmethod
    def serialize(cls, doc: dict) -> dict:
        if not doc:
            return doc
        d = dict(doc)
        for field in ('_id', 'createdBy'):
            if field in d and isinstance(d[field], ObjectId):
                d[field] = str(d[field])
        for key in ('createdAt', 'updatedAt'):
            if key in d and isinstance(d[key], datetime):
                d[key] = d[key].isoformat()
        return d