"""
Template model — SQLAlchemy/SQLite
"""
import json
from datetime import datetime, timezone
from app.database import db


class Template(db.Model):
    __tablename__ = 'templates'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False, unique=True, index=True)
    display_name  = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text,        nullable=True)
    category      = db.Column(db.String(50),  nullable=False, default='general', index=True)
    is_premium    = db.Column(db.Boolean,     nullable=False, default=False, index=True)
    is_public     = db.Column(db.Boolean,     nullable=False, default=True)
    tags          = db.Column(db.Text,        nullable=True, default='[]')    # JSON array
    thumbnail_url = db.Column(db.String(255), nullable=True)
    content       = db.Column(db.Text,        nullable=True, default='{}')   # JSON object
    usage_count   = db.Column(db.Integer,     nullable=False, default=0)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                              onupdate=lambda: datetime.now(timezone.utc))

    @classmethod
    def find_all(cls, page=1, limit=20, category=None, is_premium=None, search=None):
        q = cls.query.filter_by(is_public=True)
        if category:
            q = q.filter_by(category=category)
        if is_premium is not None:
            q = q.filter_by(is_premium=is_premium)
        if search:
            q = q.filter(
                db.or_(cls.display_name.ilike(f'%{search}%'),
                       cls.description.ilike(f'%{search}%'))
            )
        total = q.count()
        items = q.order_by(cls.usage_count.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total

    @classmethod
    def find_by_id(cls, template_id):
        return cls.query.get(int(template_id))

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name.lower()).first()

    @classmethod
    def get_categories(cls):
        rows = db.session.query(cls.category).filter_by(is_public=True).distinct().all()
        return [r[0] for r in rows]

    @classmethod
    def get_tags(cls):
        all_tags = set()
        for row in cls.query.filter_by(is_public=True).all():
            try:
                for tag in json.loads(row.tags or '[]'):
                    all_tags.add(tag)
            except Exception:
                pass
        return sorted(all_tags)

    def increment_usage(self):
        self.usage_count += 1
        db.session.commit()

    def update(self, **kwargs):
        allowed = {'display_name', 'description', 'category', 'is_premium',
                   'is_public', 'tags', 'thumbnail_url', 'content'}
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_tags_list(self):
        try:
            return json.loads(self.tags or '[]')
        except Exception:
            return []

    def get_content(self):
        try:
            return json.loads(self.content or '{}')
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id':           self.id,
            'name':         self.name,
            'displayName':  self.display_name,
            'description':  self.description,
            'category':     self.category,
            'isPremium':    self.is_premium,
            'isPublic':     self.is_public,
            'tags':         self.get_tags_list(),
            'thumbnailUrl': self.thumbnail_url,
            'content':      self.get_content(),
            'usageCount':   self.usage_count,
            'createdAt':    self.created_at.isoformat() if self.created_at else None,
            'updatedAt':    self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Template {self.name}>'