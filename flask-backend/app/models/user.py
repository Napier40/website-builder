"""
User model — SQLAlchemy/SQLite
"""
import bcrypt
from datetime import datetime, timezone
from app.database import db


class User(db.Model):
    __tablename__ = 'users'

    id                 = db.Column(db.Integer, primary_key=True)
    name               = db.Column(db.String(120), nullable=False)
    email              = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password           = db.Column(db.String(255), nullable=False)
    role               = db.Column(db.String(20),  nullable=False, default='user')  # user | admin
    subscription_type  = db.Column(db.String(50),  nullable=False, default='free')
    subscription_status= db.Column(db.String(20),  nullable=False, default='active')
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    created_at         = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at         = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                   onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    websites    = db.relationship('Website',    backref='owner',    lazy=True, cascade='all, delete-orphan',
                                  foreign_keys='Website.user_id')
    payments    = db.relationship('Payment',    backref='user',     lazy=True, cascade='all, delete-orphan')
    audit_logs  = db.relationship('AuditLog',   backref='user',     lazy=True, cascade='all, delete-orphan')
    moderations = db.relationship('Moderation', backref='reporter', lazy=True, cascade='all, delete-orphan',
                                  foreign_keys='Moderation.reporter_id')

    # ── Class methods ─────────────────────────────────────────────────────────

    @classmethod
    def create(cls, name, email, password, role='user'):
        """Hash password and persist a new user. Raises ValueError on duplicate email."""
        if cls.query.filter_by(email=email.lower().strip()).first():
            raise ValueError('Email already registered')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = cls(
            name=name.strip(),
            email=email.lower().strip(),
            password=hashed,
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.get(int(user_id))

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email.lower().strip()).first()

    @classmethod
    def find_all(cls, search=None, role=None, page=1, limit=10, sort_by='created_at', sort_dir='desc'):
        q = cls.query
        if search:
            q = q.filter(
                db.or_(cls.name.ilike(f'%{search}%'), cls.email.ilike(f'%{search}%'))
            )
        if role:
            q = q.filter_by(role=role)
        total = q.count()
        col   = getattr(cls, sort_by, cls.created_at)
        q     = q.order_by(col.desc() if sort_dir == 'desc' else col.asc())
        users = q.offset((page - 1) * limit).limit(limit).all()
        return users, total

    @classmethod
    def count(cls, role=None):
        q = cls.query
        if role:
            q = q.filter_by(role=role)
        return q.count()

    def update(self, **kwargs):
        """Update allowed fields."""
        allowed = {'name', 'role', 'subscription_type', 'subscription_status', 'stripe_customer_id'}
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    def update_password(self, new_password):
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.password = hashed
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def verify_password(self, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))

    def to_dict(self, include_password=False):
        d = {
            'id':                  self.id,
            'name':                self.name,
            'email':               self.email,
            'role':                self.role,
            'subscriptionType':    self.subscription_type,
            'subscriptionStatus':  self.subscription_status,
            'stripeCustomerId':    self.stripe_customer_id,
            'createdAt':           self.created_at.isoformat() if self.created_at else None,
            'updatedAt':           self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_password:
            d['password'] = self.password
        return d

    def __repr__(self):
        return f'<User {self.email}>'