"""
Website and Page models — SQLAlchemy/SQLite
"""
import json
from datetime import datetime, timezone
from app.database import db


class Page(db.Model):
    __tablename__ = 'pages'

    id         = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id', ondelete='CASCADE'), nullable=False)
    title      = db.Column(db.String(200), nullable=False, default='New Page')
    slug       = db.Column(db.String(200), nullable=False, default='new-page')
    # Legacy raw-HTML content (still populated for backwards compatibility).
    content    = db.Column(db.Text, nullable=False, default='')
    # New: JSON tree of the drag-and-drop canvas. When present this supersedes
    # `content` and is passed to bootstrap_renderer.render_page(). Stored as
    # TEXT (not native JSON) so SQLite + any RDBMS works identically.
    tree_json  = db.Column(db.Text, nullable=True)
    order      = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # ── Convenience accessors ──────────────────────────────────────────
    @property
    def tree(self):
        """Parsed JSON tree (or None if the page is still raw-HTML only)."""
        if not self.tree_json:
            return None
        try:
            return json.loads(self.tree_json)
        except (ValueError, TypeError):
            return None

    @tree.setter
    def tree(self, value):
        self.tree_json = json.dumps(value) if value is not None else None

    def to_dict(self):
        return {
            'id':        self.id,
            'title':     self.title,
            'slug':      self.slug,
            'content':   self.content,
            'tree':      self.tree,
            'order':     self.order,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


class Website(db.Model):
    __tablename__ = 'websites'

    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(200),  nullable=False)
    subdomain         = db.Column(db.String(100),  nullable=False, unique=True, index=True)
    custom_domain     = db.Column(db.String(255),  nullable=True,  unique=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    template          = db.Column(db.String(100),  nullable=False, default='blank')
    # Bootstrap/Bootswatch theme slug (see app.services.bootstrap_themes.THEMES).
    # "default" means the stock Bootstrap 5.3 stylesheet.
    theme             = db.Column(db.String(50),   nullable=False, default='default')
    is_published      = db.Column(db.Boolean,      nullable=False, default=False)
    moderation_status = db.Column(db.String(20),   nullable=False, default='pending')  # pending|approved|rejected
    description       = db.Column(db.Text,         nullable=True)

    # Admin override tracking
    admin_override_by     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    admin_override_at     = db.Column(db.DateTime, nullable=True)
    admin_override_reason = db.Column(db.Text,     nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    pages = db.relationship('Page', backref='website', lazy=True,
                            cascade='all, delete-orphan',
                            order_by='Page.order')

    # ── Class methods ─────────────────────────────────────────────────────────

    @classmethod
    def create(cls, name, subdomain, user_id, template='blank', theme='default'):
        """Create website with a default Home page."""
        if cls.query.filter_by(subdomain=subdomain.lower()).first():
            raise ValueError('Subdomain already taken')

        website = cls(
            name=name.strip(),
            subdomain=subdomain.lower().strip(),
            user_id=user_id,
            template=template,
            theme=theme or 'default',
        )
        db.session.add(website)
        db.session.flush()   # get website.id before adding pages

        # Add default home page
        home = Page(
            website_id=website.id,
            title='Home',
            slug='home',
            content='<h1>Welcome to my website</h1>',
            order=0,
        )
        db.session.add(home)
        db.session.commit()
        return website

    @classmethod
    def find_by_id(cls, website_id):
        return cls.query.get(int(website_id))

    @classmethod
    def find_by_user(cls, user_id, page=1, limit=10):
        q     = cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc())
        total = q.count()
        items = q.offset((page - 1) * limit).limit(limit).all()
        return items, total

    @classmethod
    def find_all(cls, page=1, limit=10, search=None, moderation_status=None):
        q = cls.query
        if search:
            q = q.filter(
                db.or_(cls.name.ilike(f'%{search}%'), cls.subdomain.ilike(f'%{search}%'))
            )
        if moderation_status:
            q = q.filter_by(moderation_status=moderation_status)
        total = q.count()
        items = q.order_by(cls.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total

    @classmethod
    def count_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).count()

    @classmethod
    def subdomain_exists(cls, subdomain, exclude_id=None):
        q = cls.query.filter_by(subdomain=subdomain.lower())
        if exclude_id:
            q = q.filter(cls.id != exclude_id)
        return q.first() is not None

    def publish(self):
        self.is_published      = True
        self.moderation_status = 'approved'
        self.updated_at        = datetime.now(timezone.utc)
        db.session.commit()

    def unpublish(self):
        self.is_published = False
        self.updated_at   = datetime.now(timezone.utc)
        db.session.commit()

    def update(self, **kwargs):
        allowed = {'name', 'description', 'custom_domain', 'moderation_status', 'template', 'theme'}
        for key, value in kwargs.items():
            if key in allowed:
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    def add_page(self, title, slug, content=''):
        page = Page(
            website_id=self.id,
            title=title,
            slug=slug,
            content=content,
            order=len(self.pages),
        )
        db.session.add(page)
        db.session.commit()
        return page

    def update_page(self, page_id, **kwargs):
        page = Page.query.filter_by(id=page_id, website_id=self.id).first()
        if not page:
            return None
        allowed = {'title', 'slug', 'content', 'order'}
        for key, value in kwargs.items():
            if key in allowed:
                setattr(page, key, value)
        # `tree` is special: coerce Python dict -> JSON string via the setter.
        if 'tree' in kwargs:
            page.tree = kwargs['tree']
        page.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return page

    def delete_page(self, page_id):
        page = Page.query.filter_by(id=page_id, website_id=self.id).first()
        if not page:
            return False
        db.session.delete(page)
        db.session.commit()
        return True

    def admin_override(self, admin_id, reason=''):
        self.admin_override_by     = admin_id
        self.admin_override_at     = datetime.now(timezone.utc)
        self.admin_override_reason = reason
        self.moderation_status     = 'approved'
        self.updated_at            = datetime.now(timezone.utc)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id':               self.id,
            'name':             self.name,
            'subdomain':        self.subdomain,
            'customDomain':     self.custom_domain,
            'userId':           self.user_id,
            'template':         self.template,
            'theme':            self.theme,
            'isPublished':      self.is_published,
            'moderationStatus': self.moderation_status,
            'description':      self.description,
            'pages':            [p.to_dict() for p in self.pages],
            'adminOverride':    {
                'by':     self.admin_override_by,
                'at':     self.admin_override_at.isoformat() if self.admin_override_at else None,
                'reason': self.admin_override_reason,
            } if self.admin_override_by else None,
            'createdAt':        self.created_at.isoformat() if self.created_at else None,
            'updatedAt':        self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Website {self.subdomain}>'