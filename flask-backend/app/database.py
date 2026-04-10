"""
Database initialisation using Flask-SQLAlchemy + SQLite.
SQLite requires no separate installation — the .db file is created
automatically on first run inside the flask-backend/ directory.
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

# Single shared SQLAlchemy instance — imported by all models
db = SQLAlchemy()


def init_db(app):
    """
    Bind the SQLAlchemy instance to the Flask app, create all tables,
    and seed default data (subscription plans, templates).
    """
    db.init_app(app)

    with app.app_context():
        # Import all models so SQLAlchemy knows about them before create_all()
        from app.models.user         import User          # noqa: F401
        from app.models.website      import Website, Page # noqa: F401
        from app.models.subscription import Subscription  # noqa: F401
        from app.models.payment      import Payment       # noqa: F401
        from app.models.audit_log    import AuditLog      # noqa: F401
        from app.models.moderation   import Moderation    # noqa: F401
        from app.models.plugin       import Plugin        # noqa: F401
        from app.models.template     import Template      # noqa: F401

        db.create_all()
        logger.info("✅ Database tables created (SQLite)")

        # Seed default data
        _seed_subscriptions()
        _seed_templates()

    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if uri == 'sqlite:///:memory:':
        logger.info("✅ Using in-memory SQLite database")
    else:
        # Extract readable path from URI
        path = uri.replace('sqlite:///', '')
        logger.info(f"✅ SQLite database ready at: {path}")


def _seed_subscriptions():
    """Insert default subscription plans if they don't exist yet."""
    from app.models.subscription import Subscription

    defaults = [
        dict(name='free',       display_name='Free',
             price=0.0,         currency='usd',
             max_websites=1,    max_pages=5,
             features='["1 website","5 pages","Basic templates","Community support"]',
             is_active=True),
        dict(name='premium',    display_name='Premium',
             price=9.99,        currency='usd',
             max_websites=5,    max_pages=50,
             features='["5 websites","50 pages","Premium templates","Priority support","Custom domain"]',
             is_active=True),
        dict(name='enterprise', display_name='Enterprise',
             price=29.99,       currency='usd',
             max_websites=999,  max_pages=999,
             features='["Unlimited websites","Unlimited pages","All templates","Dedicated support","Custom domain","API access"]',
             is_active=True),
    ]

    for plan in defaults:
        if not Subscription.query.filter_by(name=plan['name']).first():
            db.session.add(Subscription(**plan))

    try:
        db.session.commit()
        logger.info("✅ Default subscription plans seeded")
    except Exception as e:
        db.session.rollback()
        logger.warning(f"⚠️  Subscription seeding warning: {e}")


def _seed_templates():
    """Insert default website templates if none exist yet."""
    from app.models.template import Template

    if Template.query.count() > 0:
        return

    defaults = [
        dict(name='blank',      display_name='Blank Canvas',
             description='Start from scratch with a completely blank template.',
             category='basic',  is_premium=False, is_public=True,
             tags='["minimal","blank","starter"]',
             thumbnail_url='/templates/blank.png',
             content='{"pages":[{"title":"Home","slug":"home","content":"<h1>Welcome</h1>"}]}'),
        dict(name='business',   display_name='Business Pro',
             description='Professional business website template.',
             category='business', is_premium=False, is_public=True,
             tags='["business","professional","corporate"]',
             thumbnail_url='/templates/business.png',
             content='{"pages":[{"title":"Home","slug":"home","content":"<h1>Business Pro</h1>"}]}'),
        dict(name='portfolio',  display_name='Portfolio',
             description='Showcase your work with this clean portfolio template.',
             category='portfolio', is_premium=False, is_public=True,
             tags='["portfolio","creative","showcase"]',
             thumbnail_url='/templates/portfolio.png',
             content='{"pages":[{"title":"Home","slug":"home","content":"<h1>My Portfolio</h1>"}]}'),
        dict(name='blog',       display_name='Blog',
             description='Clean blogging template with article layout.',
             category='blog',  is_premium=False, is_public=True,
             tags='["blog","articles","writing"]',
             thumbnail_url='/templates/blog.png',
             content='{"pages":[{"title":"Home","slug":"home","content":"<h1>My Blog</h1>"}]}'),
        dict(name='ecommerce',  display_name='E-Commerce',
             description='Ready-made shop template with product pages.',
             category='ecommerce', is_premium=True, is_public=True,
             tags='["shop","ecommerce","products"]',
             thumbnail_url='/templates/ecommerce.png',
             content='{"pages":[{"title":"Home","slug":"home","content":"<h1>My Shop</h1>"}]}'),
    ]

    for tpl in defaults:
        db.session.add(Template(**tpl))

    try:
        db.session.commit()
        logger.info("✅ Default templates seeded")
    except Exception as e:
        db.session.rollback()
        logger.warning(f"⚠️  Template seeding warning: {e}")