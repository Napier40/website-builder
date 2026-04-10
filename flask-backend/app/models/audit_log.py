"""
Audit Log model — SQLAlchemy/SQLite
"""
import logging
from datetime import datetime, timezone
from app.database import db

logger = logging.getLogger(__name__)

VALID_ACTIONS = {
    'LOGIN', 'LOGOUT', 'REGISTER', 'CREATE', 'UPDATE', 'DELETE',
    'PUBLISH', 'UNPUBLISH', 'ADMIN_ACTION', 'MODERATION',
    'CONTENT_OVERRIDE', 'SUBSCRIPTION_CHANGE', 'PAYMENT',
}


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                               nullable=True, index=True)
    action         = db.Column(db.String(50),  nullable=False, index=True)
    resource_model = db.Column(db.String(50),  nullable=True)
    resource_id    = db.Column(db.String(50),  nullable=True)
    description    = db.Column(db.Text,        nullable=True)
    ip_address     = db.Column(db.String(50),  nullable=True)
    user_agent     = db.Column(db.String(255), nullable=True)
    timestamp      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    @classmethod
    def create_log(cls, user_id, action, resource_model=None, resource_id=None,
                   description=None, ip_address=None, user_agent=None):
        """Create an audit log entry. Failures are silently swallowed to avoid disrupting the main flow."""
        try:
            log = cls(
                user_id=user_id,
                action=action.upper(),
                resource_model=resource_model,
                resource_id=str(resource_id) if resource_id else None,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.session.add(log)
            db.session.commit()
            return log
        except Exception as e:
            db.session.rollback()
            logger.warning(f"⚠️  Audit log creation failed (non-fatal): {e}")
            return None

    @classmethod
    def find_all(cls, page=1, limit=50, action=None, user_id=None):
        q = cls.query
        if action:
            q = q.filter_by(action=action.upper())
        if user_id:
            q = q.filter_by(user_id=user_id)
        total = q.count()
        items = q.order_by(cls.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total

    @classmethod
    def find_by_user(cls, user_id, limit=20):
        return cls.query.filter_by(user_id=user_id)\
                        .order_by(cls.timestamp.desc())\
                        .limit(limit).all()

    def to_dict(self):
        return {
            'id':            self.id,
            'userId':        self.user_id,
            'action':        self.action,
            'resourceModel': self.resource_model,
            'resourceId':    self.resource_id,
            'description':   self.description,
            'ipAddress':     self.ip_address,
            'userAgent':     self.user_agent,
            'timestamp':     self.timestamp.isoformat() if self.timestamp else None,
        }

    def __repr__(self):
        return f'<AuditLog {self.action} user={self.user_id}>'