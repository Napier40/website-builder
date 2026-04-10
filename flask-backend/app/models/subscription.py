"""
Subscription Plan model — SQLAlchemy/SQLite
"""
import json
from datetime import datetime, timezone
from app.database import db


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(50),  nullable=False, unique=True, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    price        = db.Column(db.Float,       nullable=False, default=0.0)
    currency     = db.Column(db.String(10),  nullable=False, default='usd')
    max_websites = db.Column(db.Integer,     nullable=False, default=1)
    max_pages    = db.Column(db.Integer,     nullable=False, default=5)
    features     = db.Column(db.Text,        nullable=False, default='[]')  # JSON array
    is_active    = db.Column(db.Boolean,     nullable=False, default=True)
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                             onupdate=lambda: datetime.now(timezone.utc))

    @classmethod
    def find_all_active(cls):
        return cls.query.filter_by(is_active=True).order_by(cls.price.asc()).all()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name.lower()).first()

    @classmethod
    def find_by_id(cls, plan_id):
        return cls.query.get(int(plan_id))

    def update(self, **kwargs):
        allowed = {'display_name', 'price', 'currency', 'max_websites',
                   'max_pages', 'features', 'is_active'}
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    def get_features(self):
        try:
            return json.loads(self.features)
        except Exception:
            return []

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'displayName': self.display_name,
            'price':       self.price,
            'currency':    self.currency,
            'maxWebsites': self.max_websites,
            'maxPages':    self.max_pages,
            'features':    self.get_features(),
            'isActive':    self.is_active,
            'createdAt':   self.created_at.isoformat() if self.created_at else None,
            'updatedAt':   self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Subscription {self.name}>'