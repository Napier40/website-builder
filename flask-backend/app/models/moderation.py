"""
Moderation model — SQLAlchemy/SQLite
"""
from datetime import datetime, timezone
from app.database import db


class Moderation(db.Model):
    __tablename__ = 'moderation'

    id               = db.Column(db.Integer, primary_key=True)
    content_id       = db.Column(db.String(50),  nullable=False)
    content_model    = db.Column(db.String(50),  nullable=False, index=True)
    reporter_id      = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
                                 nullable=True)
    reason           = db.Column(db.Text,        nullable=False)
    status           = db.Column(db.String(20),  nullable=False, default='pending', index=True)
    reviewed_by      = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
                                 nullable=True)
    reviewed_at      = db.Column(db.DateTime,    nullable=True)
    review_notes     = db.Column(db.Text,        nullable=True)
    original_content = db.Column(db.Text,        nullable=True)
    created_at       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                 onupdate=lambda: datetime.now(timezone.utc))

    reviewer = db.relationship('User', foreign_keys='Moderation.reviewed_by', lazy=True)

    @classmethod
    def create(cls, content_id, content_model, reporter_id, reason, original_content=None):
        mod = cls(
            content_id=str(content_id),
            content_model=content_model,
            reporter_id=reporter_id,
            reason=reason,
            original_content=original_content,
        )
        db.session.add(mod)
        db.session.commit()
        return mod

    @classmethod
    def find_by_id(cls, mod_id):
        return cls.query.get(int(mod_id))

    @classmethod
    def find_all(cls, page=1, limit=10, status=None):
        q = cls.query
        if status:
            q = q.filter_by(status=status)
        total = q.count()
        items = q.order_by(cls.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total

    def review(self, admin_id, status, notes=''):
        self.status      = status
        self.reviewed_by = admin_id
        self.reviewed_at = datetime.now(timezone.utc)
        self.review_notes = notes
        self.updated_at  = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self):
        return {
            'id':              self.id,
            'contentId':       self.content_id,
            'contentModel':    self.content_model,
            'reporterId':      self.reporter_id,
            'reason':          self.reason,
            'status':          self.status,
            'reviewedBy':      self.reviewed_by,
            'reviewedAt':      self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewNotes':     self.review_notes,
            'originalContent': self.original_content,
            'createdAt':       self.created_at.isoformat() if self.created_at else None,
            'updatedAt':       self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Moderation {self.id} {self.status}>'