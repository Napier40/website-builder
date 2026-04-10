"""
Plugin model — SQLAlchemy/SQLite
"""
import json
from datetime import datetime, timezone
from app.database import db


class Plugin(db.Model):
    __tablename__ = 'plugins'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False, unique=True, index=True)
    display_name = db.Column(db.String(200), nullable=False)
    description  = db.Column(db.Text,        nullable=True)
    version      = db.Column(db.String(20),  nullable=False, default='1.0.0')
    author       = db.Column(db.String(100), nullable=True)
    is_active    = db.Column(db.Boolean,     nullable=False, default=False, index=True)
    config       = db.Column(db.Text,        nullable=True, default='{}')  # JSON object
    hooks        = db.Column(db.Text,        nullable=True, default='[]')  # JSON array
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                             onupdate=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, name, display_name, description=None, version='1.0.0',
               author=None, config=None, hooks=None):
        plugin = cls(
            name=name.lower().strip(),
            display_name=display_name,
            description=description,
            version=version,
            author=author,
            config=json.dumps(config or {}),
            hooks=json.dumps(hooks or []),
        )
        db.session.add(plugin)
        db.session.commit()
        return plugin

    @classmethod
    def find_all(cls, active_only=False):
        q = cls.query
        if active_only:
            q = q.filter_by(is_active=True)
        return q.order_by(cls.name.asc()).all()

    @classmethod
    def find_by_id(cls, plugin_id):
        return cls.query.get(int(plugin_id))

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name.lower()).first()

    def toggle_active(self):
        self.is_active  = not self.is_active
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return self.is_active

    def update(self, **kwargs):
        allowed = {'display_name', 'description', 'version', 'author', 'is_active', 'config', 'hooks'}
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_config(self):
        try:
            return json.loads(self.config or '{}')
        except Exception:
            return {}

    def get_hooks(self):
        try:
            return json.loads(self.hooks or '[]')
        except Exception:
            return []

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'displayName': self.display_name,
            'description': self.description,
            'version':     self.version,
            'author':      self.author,
            'isActive':    self.is_active,
            'config':      self.get_config(),
            'hooks':       self.get_hooks(),
            'createdAt':   self.created_at.isoformat() if self.created_at else None,
            'updatedAt':   self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Plugin {self.name}>'