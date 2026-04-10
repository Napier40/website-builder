"""
Website Model
Handles all website and page-related database operations using PyMongo
"""
import logging
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db

logger = logging.getLogger(__name__)

VALID_MODERATION_STATUSES = ['pending', 'approved', 'rejected', 'flagged']


class WebsiteModel:
    """Website model providing CRUD operations and page management."""

    COLLECTION = 'websites'

    @classmethod
    def get_collection(cls):
        return get_db()[cls.COLLECTION]

    # ─── Default content ───────────────────────────────────────────────────────

    @classmethod
    def default_home_page(cls) -> dict:
        """Return a default homepage structure for new websites."""
        now = datetime.now(timezone.utc)
        return {
            '_id': ObjectId(),
            'title': 'Home',
            'slug': 'home',
            'content': {
                'sections': [
                    {
                        'type': 'hero',
                        'heading': 'Welcome to my website',
                        'subheading': 'This is a new website created with Website Builder',
                        'buttonText': 'Learn More',
                        'buttonLink': '#about'
                    },
                    {
                        'type': 'text',
                        'heading': 'About Us',
                        'content': 'This is the about section. You can edit this in the website builder.'
                    }
                ]
            },
            'isPublished': True,
            'meta': {
                'description': 'Welcome to my website',
                'keywords': 'website, builder'
            },
            'createdAt': now,
            'updatedAt': now
        }

    @classmethod
    def default_settings(cls) -> dict:
        """Return default theme/SEO settings for a new website."""
        return {
            'theme': {
                'primaryColor': '#3498db',
                'secondaryColor': '#2ecc71',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '16px'
            },
            'seo': {
                'title': '',
                'description': '',
                'keywords': ''
            },
            'analytics': {
                'googleAnalyticsId': ''
            }
        }

    # ─── Create ────────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, name: str, subdomain: str, user_id: str,
               template: str = 'default') -> dict:
        """Create a new website with a default home page."""
        collection = cls.get_collection()

        if collection.find_one({'subdomain': subdomain.lower().strip()}):
            raise ValueError('Subdomain is already taken')

        now = datetime.now(timezone.utc)
        doc = {
            'name': name.strip(),
            'subdomain': subdomain.lower().strip(),
            'customDomain': None,
            'user': ObjectId(user_id),
            'template': template,
            'pages': [cls.default_home_page()],
            'settings': cls.default_settings(),
            'isPublished': False,
            'moderationStatus': 'approved',
            'moderationReason': None,
            'adminOverride': {
                'admin': None,
                'date': None,
                'reason': None
            },
            'lastModifiedBy': None,
            'lastModifiedAt': None,
            'createdAt': now,
            'updatedAt': now
        }

        result = collection.insert_one(doc)
        doc['_id'] = result.inserted_id
        return cls.serialize(doc)

    # ─── Read ──────────────────────────────────────────────────────────────────

    @classmethod
    def find_by_id(cls, website_id: str) -> dict | None:
        """Find a website by its MongoDB ObjectId string."""
        try:
            doc = cls.get_collection().find_one({'_id': ObjectId(website_id)})
            return cls.serialize(doc) if doc else None
        except Exception:
            return None

    @classmethod
    def find_by_user(cls, user_id: str) -> list:
        """Find all websites belonging to a specific user."""
        cursor = cls.get_collection().find({'user': ObjectId(user_id)})
        return [cls.serialize(doc) for doc in cursor]

    @classmethod
    def find_all(cls, query: dict = None, skip: int = 0, limit: int = 10,
                 sort_field: str = 'createdAt', sort_dir: int = -1) -> tuple[list, int]:
        """Find all websites with pagination. Returns (websites, total)."""
        collection = cls.get_collection()
        query = query or {}
        total = collection.count_documents(query)
        cursor = collection.find(query).sort(sort_field, sort_dir).skip(skip).limit(limit)
        return [cls.serialize(doc) for doc in cursor], total

    @classmethod
    def count_by_user(cls, user_id: str) -> int:
        """Count websites belonging to a user."""
        return cls.get_collection().count_documents({'user': ObjectId(user_id)})

    @classmethod
    def subdomain_exists(cls, subdomain: str, exclude_id: str = None) -> bool:
        """Check whether a subdomain is already in use."""
        query = {'subdomain': subdomain.lower().strip()}
        if exclude_id:
            query['_id'] = {'$ne': ObjectId(exclude_id)}
        return cls.get_collection().find_one(query) is not None

    @classmethod
    def domain_exists(cls, domain: str, exclude_id: str = None) -> bool:
        """Check whether a custom domain is already in use."""
        query = {'customDomain': domain}
        if exclude_id:
            query['_id'] = {'$ne': ObjectId(exclude_id)}
        return cls.get_collection().find_one(query) is not None

    # ─── Update ────────────────────────────────────────────────────────────────

    @classmethod
    def update_by_id(cls, website_id: str, updates: dict) -> dict | None:
        """Update a website by ID."""
        updates['updatedAt'] = datetime.now(timezone.utc)
        result = cls.get_collection().find_one_and_update(
            {'_id': ObjectId(website_id)},
            {'$set': updates},
            return_document=True
        )
        return cls.serialize(result) if result else None

    @classmethod
    def publish(cls, website_id: str) -> dict | None:
        """Mark a website as published."""
        return cls.update_by_id(website_id, {'isPublished': True})

    @classmethod
    def unpublish(cls, website_id: str) -> dict | None:
        """Mark a website as unpublished."""
        return cls.update_by_id(website_id, {'isPublished': False})

    # ─── Page management ──────────────────────────────────────────────────────

    @classmethod
    def add_page(cls, website_id: str, page_data: dict) -> dict | None:
        """Add a new page to a website's pages array."""
        now = datetime.now(timezone.utc)
        new_page = {
            '_id': ObjectId(),
            'title': page_data.get('title', 'New Page'),
            'slug': page_data.get('slug', ''),
            'content': page_data.get('content', {}),
            'isPublished': page_data.get('isPublished', False),
            'meta': page_data.get('meta', {}),
            'createdAt': now,
            'updatedAt': now
        }

        result = cls.get_collection().find_one_and_update(
            {'_id': ObjectId(website_id)},
            {
                '$push': {'pages': new_page},
                '$set': {'updatedAt': now}
            },
            return_document=True
        )
        if result:
            # Return the newly added page serialized
            for page in result.get('pages', []):
                if str(page.get('_id')) == str(new_page['_id']):
                    return cls._serialize_page(page)
        return None

    @classmethod
    def update_page(cls, website_id: str, page_id: str, updates: dict) -> dict | None:
        """Update a specific page within a website."""
        now = datetime.now(timezone.utc)

        set_fields = {}
        for field in ('title', 'content', 'isPublished', 'meta'):
            if field in updates:
                set_fields[f'pages.$.{field}'] = updates[field]
        set_fields['pages.$.updatedAt'] = now
        set_fields['updatedAt'] = now

        result = cls.get_collection().find_one_and_update(
            {
                '_id': ObjectId(website_id),
                'pages._id': ObjectId(page_id)
            },
            {'$set': set_fields},
            return_document=True
        )

        if result:
            for page in result.get('pages', []):
                if str(page.get('_id')) == page_id:
                    return cls._serialize_page(page)
        return None

    @classmethod
    def delete_page(cls, website_id: str, page_id: str) -> bool:
        """Remove a page from a website. Returns True if successful."""
        now = datetime.now(timezone.utc)
        result = cls.get_collection().update_one(
            {'_id': ObjectId(website_id)},
            {
                '$pull': {'pages': {'_id': ObjectId(page_id)}},
                '$set': {'updatedAt': now}
            }
        )
        return result.modified_count > 0

    # ─── Admin ────────────────────────────────────────────────────────────────

    @classmethod
    def admin_override(cls, website_id: str, admin_id: str,
                       new_pages: list, reason: str) -> dict | None:
        """
        Admin override: replace website pages and record the override.
        """
        now = datetime.now(timezone.utc)
        result = cls.get_collection().find_one_and_update(
            {'_id': ObjectId(website_id)},
            {'$set': {
                'pages': new_pages,
                'lastModifiedBy': ObjectId(admin_id),
                'lastModifiedAt': now,
                'adminOverride': {
                    'admin': ObjectId(admin_id),
                    'date': now,
                    'reason': reason
                },
                'updatedAt': now
            }},
            return_document=True
        )
        return cls.serialize(result) if result else None

    # ─── Delete ────────────────────────────────────────────────────────────────

    @classmethod
    def delete_by_id(cls, website_id: str) -> bool:
        """Delete a website by ID."""
        result = cls.get_collection().delete_one({'_id': ObjectId(website_id)})
        return result.deleted_count > 0

    @classmethod
    def count(cls, query: dict = None) -> int:
        """Count websites matching a query."""
        return cls.get_collection().count_documents(query or {})

    # ─── Serialization ────────────────────────────────────────────────────────

    @classmethod
    def _serialize_page(cls, page: dict) -> dict:
        """Serialize a single page document."""
        p = dict(page)
        if '_id' in p and isinstance(p['_id'], ObjectId):
            p['_id'] = str(p['_id'])
        for key in ('createdAt', 'updatedAt'):
            if key in p and isinstance(p[key], datetime):
                p[key] = p[key].isoformat()
        return p

    @classmethod
    def serialize(cls, doc: dict) -> dict:
        """Recursively serialize a website document for JSON output."""
        if not doc:
            return doc
        d = dict(doc)

        # Top-level ObjectId fields
        for field in ('_id', 'user', 'lastModifiedBy'):
            if field in d and isinstance(d[field], ObjectId):
                d[field] = str(d[field])

        # adminOverride nested ObjectIds
        if 'adminOverride' in d and d['adminOverride']:
            ao = dict(d['adminOverride'])
            if isinstance(ao.get('admin'), ObjectId):
                ao['admin'] = str(ao['admin'])
            if isinstance(ao.get('date'), datetime):
                ao['date'] = ao['date'].isoformat()
            d['adminOverride'] = ao

        # Datetime fields
        for key in ('createdAt', 'updatedAt', 'lastModifiedAt'):
            if key in d and isinstance(d[key], datetime):
                d[key] = d[key].isoformat()

        # Serialize pages array
        if 'pages' in d and d['pages']:
            d['pages'] = [cls._serialize_page(p) for p in d['pages']]

        return d