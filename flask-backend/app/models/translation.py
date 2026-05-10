"""
Translation model — SQLAlchemy/SQLite
Supports multilingual interface with English as the principal/fallback language.
"""
import json
from datetime import datetime, timezone
from app.database import db


class Translation(db.Model):
    """
    Stores UI translations by key and language.
    English ('en') is the principal language and fallback.
    """
    __tablename__ = 'translations'

    id        = db.Column(db.Integer, primary_key=True)
    key       = db.Column(db.String(255), nullable=False, index=True)
    language  = db.Column(db.String(10),  nullable=False, index=True)
    value     = db.Column(db.Text,       nullable=False)
    namespace = db.Column(db.String(50),  nullable=True,   index=True)  # e.g., 'builder', 'common'
    context   = db.Column(db.Text,       nullable=True)   # Extra context for translators

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # --- Composite unique constraint ---
    __table_args__ = (
        db.UniqueConstraint('key', 'language', 'namespace', name='_key_lang_ns_unique'),
    )

    # --- Class methods ---

    @classmethod
    def find_by_key(cls, key, language='en', namespace=None):
        """
        Find a translation by key and language.
        Falls back to English if the requested language doesn't exist.
        """
        q = cls.query.filter_by(key=key)
        if namespace:
            q = q.filter_by(namespace=namespace)

        # Try requested language first
        row = q.filter_by(language=language.lower()).first()

        # Fallback to English
        if not row and language.lower() != 'en':
            row = q.filter_by(language='en').first()

        return row

    @classmethod
    def get_all_by_language(cls, language='en', namespace=None):
        """
        Get all translations for a language as a nested dictionary.
        Structure: {namespace: {key: value}} or {key: value} if no namespace.
        """
        q = cls.query
        if namespace:
            q = q.filter_by(namespace=namespace)
        rows = q.filter_by(language=language.lower()).all()

        if namespace:
            return {row.key: row.value for row in rows}
        else:
            # Group by namespace
            result = {}
            for row in rows:
                ns = row.namespace or 'common'
                if ns not in result:
                    result[ns] = {}
                result[ns][row.key] = row.value
            return result

    @classmethod
    def upsert(cls, key, language, value, namespace=None, context=None):
        """
        Insert or update a translation.
        """
        from app.database import db

        row = cls.query.filter_by(key=key, language=language.lower(), namespace=namespace).first()
        if row:
            row.value = value
            if context is not None:
                row.context = context
            row.updated_at = datetime.now(timezone.utc)
        else:
            row = cls(
                key=key,
                language=language.lower(),
                value=value,
                namespace=namespace,
                context=context,
            )
            db.session.add(row)
        db.session.commit()
        return row

    @classmethod
    def bulk_upsert(cls, translations, language='en'):
        """
        Bulk insert/update translations.
        translations format:
            {
                key: value,
                ...
            }
        or
            {
                namespace: {
                    key: value,
                    ...
                },
                ...
            }
        Returns the number of translations processed.
        """
        from app.database import db

        count = 0
        lang = language.lower()

        # Detect format
        if translations and isinstance(next(iter(translations.values())), dict):
            # Grouped by namespace
            for namespace, items in translations.items():
                for key, value in items.items():
                    cls.upsert(key, lang, value, namespace)
                    count += 1
        else:
            # Flat dictionary
            for key, value in translations.items():
                cls.upsert(key, lang, value, namespace=None)
                count += 1

        return count

    @classmethod
    def get_supported_languages(cls):
        """
        Return list of available language codes.
        """
        rows = cls.query.with_entities(cls.language).distinct().all()
        return [r[0] for r in rows]

    # --- Instance methods ---

    def to_dict(self):
        return {
            'id':        self.id,
            'key':       self.key,
            'language':  self.language,
            'value':     self.value,
            'namespace': self.namespace,
            'context':   self.context,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Translation {self.key}:{self.language}>'