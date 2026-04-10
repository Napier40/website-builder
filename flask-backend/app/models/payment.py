"""
Payment model — SQLAlchemy/SQLite
"""
from datetime import datetime, timezone
from app.database import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id                       = db.Column(db.Integer, primary_key=True)
    user_id                  = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                                         nullable=False, index=True)
    amount                   = db.Column(db.Float,      nullable=False)
    currency                 = db.Column(db.String(10), nullable=False, default='usd')
    status                   = db.Column(db.String(30), nullable=False, default='pending')
    stripe_payment_intent_id = db.Column(db.String(200), nullable=True, index=True)
    subscription_type        = db.Column(db.String(50),  nullable=True)
    description              = db.Column(db.Text,        nullable=True)
    created_at               = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at               = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                         onupdate=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, user_id, amount, currency='usd', status='pending',
               stripe_payment_intent_id=None, subscription_type=None, description=None):
        payment = cls(
            user_id=user_id,
            amount=amount,
            currency=currency,
            status=status,
            stripe_payment_intent_id=stripe_payment_intent_id,
            subscription_type=subscription_type,
            description=description,
        )
        db.session.add(payment)
        db.session.commit()
        return payment

    @classmethod
    def find_by_id(cls, payment_id):
        return cls.query.get(int(payment_id))

    @classmethod
    def find_by_user(cls, user_id, page=1, limit=10):
        q     = cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc())
        total = q.count()
        items = q.offset((page - 1) * limit).limit(limit).all()
        return items, total

    @classmethod
    def find_all(cls, page=1, limit=10):
        q     = cls.query.order_by(cls.created_at.desc())
        total = q.count()
        items = q.offset((page - 1) * limit).limit(limit).all()
        return items, total

    @classmethod
    def find_by_stripe_id(cls, stripe_id):
        return cls.query.filter_by(stripe_payment_intent_id=stripe_id).first()

    def update_status(self, status):
        self.status     = status
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self):
        return {
            'id':                     self.id,
            'userId':                 self.user_id,
            'amount':                 self.amount,
            'currency':               self.currency,
            'status':                 self.status,
            'stripePaymentIntentId':  self.stripe_payment_intent_id,
            'subscriptionType':       self.subscription_type,
            'description':            self.description,
            'createdAt':              self.created_at.isoformat() if self.created_at else None,
            'updatedAt':              self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Payment {self.id} {self.status}>'