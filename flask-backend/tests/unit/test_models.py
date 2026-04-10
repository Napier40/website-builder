"""
Unit tests for SQLAlchemy models (in-memory SQLite)
"""
import pytest
from app import create_app
from app.database import db as _db


@pytest.fixture(scope='function')
def app_ctx():
    """Fresh in-memory SQLite for each test."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


# ── User model ────────────────────────────────────────────────────────────────

class TestUserModel:

    def test_create_user(self, app_ctx):
        from app.models.user import User
        user = User.create(name='Alice', email='alice@example.com', password='secret123')
        assert user.id is not None
        assert user.name == 'Alice'
        assert user.email == 'alice@example.com'
        assert user.role == 'user'
        assert user.subscription_type == 'free'

    def test_password_is_hashed(self, app_ctx):
        from app.models.user import User
        user = User.create(name='Bob', email='bob@example.com', password='mypassword')
        assert user.password != 'mypassword'
        assert user.verify_password('mypassword')

    def test_wrong_password_rejected(self, app_ctx):
        from app.models.user import User
        user = User.create(name='Carol', email='carol@example.com', password='correct')
        assert not user.verify_password('wrong')

    def test_duplicate_email_raises(self, app_ctx):
        from app.models.user import User
        User.create(name='Dave', email='dave@example.com', password='pass123')
        with pytest.raises(ValueError, match='already registered'):
            User.create(name='Dave2', email='dave@example.com', password='pass456')

    def test_find_by_email(self, app_ctx):
        from app.models.user import User
        User.create(name='Eve', email='eve@example.com', password='pass123')
        user = User.find_by_email('eve@example.com')
        assert user is not None
        assert user.name == 'Eve'

    def test_find_by_email_case_insensitive(self, app_ctx):
        from app.models.user import User
        User.create(name='Frank', email='frank@example.com', password='pass123')
        user = User.find_by_email('FRANK@EXAMPLE.COM')
        assert user is not None

    def test_find_by_id(self, app_ctx):
        from app.models.user import User
        created = User.create(name='Grace', email='grace@example.com', password='pass123')
        found   = User.find_by_id(created.id)
        assert found is not None
        assert found.email == 'grace@example.com'

    def test_update_user(self, app_ctx):
        from app.models.user import User
        user = User.create(name='Hank', email='hank@example.com', password='pass123')
        user.update(name='Hank Updated', subscription_type='premium')
        refreshed = User.find_by_id(user.id)
        assert refreshed.name == 'Hank Updated'
        assert refreshed.subscription_type == 'premium'

    def test_update_password(self, app_ctx):
        from app.models.user import User
        user = User.create(name='Iris', email='iris@example.com', password='oldpass')
        user.update_password('newpass123')
        assert user.verify_password('newpass123')
        assert not user.verify_password('oldpass')

    def test_delete_user(self, app_ctx):
        from app.models.user import User
        user = User.create(name='Jack', email='jack@example.com', password='pass123')
        uid  = user.id
        user.delete()
        assert User.find_by_id(uid) is None

    def test_to_dict_no_password(self, app_ctx):
        from app.models.user import User
        user = User.create(name='Kate', email='kate@example.com', password='pass123')
        d    = user.to_dict()
        assert 'password' not in d
        assert d['email'] == 'kate@example.com'

    def test_create_admin(self, app_ctx):
        from app.models.user import User
        admin = User.create(name='Admin', email='admin@example.com',
                            password='admin123', role='admin')
        assert admin.role == 'admin'

    def test_count(self, app_ctx):
        from app.models.user import User
        User.create(name='U1', email='u1@example.com', password='pass')
        User.create(name='U2', email='u2@example.com', password='pass')
        assert User.count() == 2

    def test_find_all(self, app_ctx):
        from app.models.user import User
        User.create(name='L1', email='l1@example.com', password='pass')
        User.create(name='L2', email='l2@example.com', password='pass')
        users, total = User.find_all()
        assert total == 2
        assert len(users) == 2


# ── Website model ─────────────────────────────────────────────────────────────

class TestWebsiteModel:

    def _make_user(self):
        from app.models.user import User
        return User.create(name='Owner', email='owner@example.com', password='pass123')

    def test_create_website(self, app_ctx):
        from app.models.website import Website
        user = self._make_user()
        site = Website.create(name='My Site', subdomain='my-site', user_id=user.id)
        assert site.id is not None
        assert site.subdomain == 'my-site'
        assert len(site.pages) == 1
        assert site.pages[0].slug == 'home'

    def test_duplicate_subdomain_raises(self, app_ctx):
        from app.models.website import Website
        user = self._make_user()
        Website.create(name='Site 1', subdomain='taken', user_id=user.id)
        with pytest.raises(ValueError, match='Subdomain'):
            Website.create(name='Site 2', subdomain='taken', user_id=user.id)

    def test_publish_website(self, app_ctx):
        from app.models.website import Website
        user = self._make_user()
        site = Website.create(name='Pub Site', subdomain='pub-site', user_id=user.id)
        assert not site.is_published
        site.publish()
        assert site.is_published

    def test_unpublish_website(self, app_ctx):
        from app.models.website import Website
        user = self._make_user()
        site = Website.create(name='Unpub', subdomain='unpub-site', user_id=user.id)
        site.publish()
        site.unpublish()
        assert not site.is_published

    def test_add_page(self, app_ctx):
        from app.models.website import Website
        user = self._make_user()
        site = Website.create(name='Pages Site', subdomain='pages-site', user_id=user.id)
        page = site.add_page('About', 'about', '<h1>About</h1>')
        assert page.id is not None
        assert len(site.pages) == 2

    def test_update_page(self, app_ctx):
        from app.models.website import Website
        user = self._make_user()
        site = Website.create(name='Update Page', subdomain='update-page', user_id=user.id)
        page = site.pages[0]
        updated = site.update_page(page.id, title='Updated Home', content='<p>new</p>')
        assert updated.title == 'Updated Home'

    def test_delete_page(self, app_ctx):
        from app.models.website import Website
        user = self._make_user()
        site = Website.create(name='Del Page', subdomain='del-page', user_id=user.id)
        page_id = site.pages[0].id
        result  = site.delete_page(page_id)
        assert result is True

    def test_count_by_user(self, app_ctx):
        from app.models.website import Website
        user = self._make_user()
        Website.create(name='S1', subdomain='s1', user_id=user.id)
        Website.create(name='S2', subdomain='s2', user_id=user.id)
        assert Website.count_by_user(user.id) == 2

    def test_to_dict(self, app_ctx):
        from app.models.website import Website
        user = self._make_user()
        site = Website.create(name='Dict Site', subdomain='dict-site', user_id=user.id)
        d    = site.to_dict()
        assert d['subdomain'] == 'dict-site'
        assert isinstance(d['pages'], list)


# ── Subscription model ────────────────────────────────────────────────────────

class TestSubscriptionModel:

    def test_default_plans_seeded(self, app_ctx):
        from app.models.subscription import Subscription
        plans = Subscription.find_all_active()
        names = [p.name for p in plans]
        assert 'free'       in names
        assert 'premium'    in names
        assert 'enterprise' in names

    def test_find_by_name(self, app_ctx):
        from app.models.subscription import Subscription
        plan = Subscription.find_by_name('free')
        assert plan is not None
        assert plan.price == 0.0

    def test_premium_plan(self, app_ctx):
        from app.models.subscription import Subscription
        plan = Subscription.find_by_name('premium')
        assert plan.price > 0
        assert plan.max_websites > 1

    def test_features_returns_list(self, app_ctx):
        from app.models.subscription import Subscription
        plan = Subscription.find_by_name('free')
        assert isinstance(plan.get_features(), list)

    def test_to_dict(self, app_ctx):
        from app.models.subscription import Subscription
        plan = Subscription.find_by_name('enterprise')
        d    = plan.to_dict()
        assert d['name']        == 'enterprise'
        assert d['maxWebsites'] == 999