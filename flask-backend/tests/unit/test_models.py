"""
Unit Tests - Models
Tests for UserModel, WebsiteModel, SubscriptionModel
"""
import pytest
from bson import ObjectId


class TestUserModel:
    """Tests for the UserModel class."""

    def test_create_user(self, flask_app, clean_db):
        """Test creating a new user."""
        with flask_app.app_context():
            from app.models.user import UserModel
            user = UserModel.create('Alice', 'alice@example.com', 'password123')

            assert user is not None
            assert user['name'] == 'Alice'
            assert user['email'] == 'alice@example.com'
            assert 'password' not in user  # password must be removed from sanitized output
            assert user['role'] == 'user'
            assert user['subscriptionStatus'] == 'none'
            assert user['isActive'] is True
            assert '_id' in user

    def test_create_user_normalizes_email(self, flask_app, clean_db):
        """Email should be lowercased and stripped."""
        with flask_app.app_context():
            from app.models.user import UserModel
            user = UserModel.create('Bob', '  Bob@Example.COM  ', 'password123')
            assert user['email'] == 'bob@example.com'

    def test_create_duplicate_email_raises(self, flask_app, clean_db):
        """Creating two users with the same email should raise ValueError."""
        with flask_app.app_context():
            from app.models.user import UserModel
            UserModel.create('Alice', 'alice@example.com', 'password123')
            with pytest.raises(ValueError, match='already exists'):
                UserModel.create('Alice2', 'alice@example.com', 'password456')

    def test_find_by_email(self, flask_app, registered_user):
        """Should find a user by email address."""
        with flask_app.app_context():
            from app.models.user import UserModel
            found = UserModel.find_by_email('testuser@example.com', include_password=False)
            assert found is not None
            assert found['email'] == 'testuser@example.com'
            assert 'password' not in found

    def test_find_by_email_not_found(self, flask_app, clean_db):
        """Should return None when user not found."""
        with flask_app.app_context():
            from app.models.user import UserModel
            result = UserModel.find_by_email('nobody@example.com')
            assert result is None

    def test_verify_password_correct(self, flask_app, clean_db):
        """Should return True for the correct password."""
        with flask_app.app_context():
            from app.models.user import UserModel
            UserModel.create('Carol', 'carol@example.com', 'securePass!')
            user_with_pw = UserModel.find_by_email('carol@example.com', include_password=True)
            assert UserModel.verify_password('securePass!', user_with_pw['password']) is True

    def test_verify_password_wrong(self, flask_app, clean_db):
        """Should return False for an incorrect password."""
        with flask_app.app_context():
            from app.models.user import UserModel
            UserModel.create('Dave', 'dave@example.com', 'correctPass')
            user_with_pw = UserModel.find_by_email('dave@example.com', include_password=True)
            assert UserModel.verify_password('wrongPass', user_with_pw['password']) is False

    def test_update_user(self, flask_app, registered_user):
        """Should update user fields."""
        with flask_app.app_context():
            from app.models.user import UserModel
            updated = UserModel.update_by_id(
                registered_user['_id'],
                {'name': 'Updated Name', 'subscriptionStatus': 'basic'}
            )
            assert updated['name'] == 'Updated Name'
            assert updated['subscriptionStatus'] == 'basic'

    def test_update_password(self, flask_app, registered_user):
        """Should update password and verify new one works."""
        with flask_app.app_context():
            from app.models.user import UserModel
            success = UserModel.update_password(registered_user['_id'], 'NewPassword456')
            assert success is True

            user_with_pw = UserModel.find_by_email(
                registered_user['email'], include_password=True
            )
            assert UserModel.verify_password('NewPassword456', user_with_pw['password']) is True

    def test_delete_user(self, flask_app, registered_user):
        """Should delete a user and return True."""
        with flask_app.app_context():
            from app.models.user import UserModel
            deleted = UserModel.delete_by_id(registered_user['_id'])
            assert deleted is True
            found = UserModel.find_by_id(registered_user['_id'])
            assert found is None

    def test_count(self, flask_app, registered_user):
        """Should correctly count users."""
        with flask_app.app_context():
            from app.models.user import UserModel
            count = UserModel.count()
            assert count == 1

    def test_sanitize_removes_password(self, flask_app, clean_db):
        """Sanitize must remove the password field."""
        with flask_app.app_context():
            from app.models.user import UserModel
            doc = {
                '_id': ObjectId(),
                'name': 'Eve',
                'email': 'eve@example.com',
                'password': 'should_be_removed'
            }
            sanitized = UserModel.sanitize(doc)
            assert 'password' not in sanitized
            assert sanitized['name'] == 'Eve'


class TestWebsiteModel:
    """Tests for the WebsiteModel class."""

    def test_create_website(self, flask_app, registered_user, clean_db):
        """Should create a website with a default home page."""
        with flask_app.app_context():
            from app.models.website import WebsiteModel
            website = WebsiteModel.create(
                name='My Site',
                subdomain='my-site-abc',
                user_id=str(registered_user['_id'])
            )

            assert website is not None
            assert website['name'] == 'My Site'
            assert website['subdomain'] == 'my-site-abc'
            assert website['isPublished'] is False
            assert len(website['pages']) == 1
            assert website['pages'][0]['slug'] == 'home'

    def test_create_duplicate_subdomain_raises(self, flask_app, registered_user, clean_db):
        """Creating two websites with the same subdomain should raise ValueError."""
        with flask_app.app_context():
            from app.models.website import WebsiteModel
            WebsiteModel.create('Site A', 'dupe-sub', str(registered_user['_id']))
            with pytest.raises(ValueError, match='already taken'):
                WebsiteModel.create('Site B', 'dupe-sub', str(registered_user['_id']))

    def test_find_by_user(self, flask_app, registered_user, registered_website):
        """Should find all websites belonging to a user."""
        with flask_app.app_context():
            from app.models.website import WebsiteModel
            sites = WebsiteModel.find_by_user(str(registered_user['_id']))
            assert len(sites) == 1
            assert sites[0]['name'] == registered_website['name']

    def test_publish_website(self, flask_app, registered_website):
        """Should set isPublished to True."""
        with flask_app.app_context():
            from app.models.website import WebsiteModel
            updated = WebsiteModel.publish(registered_website['_id'])
            assert updated['isPublished'] is True

    def test_unpublish_website(self, flask_app, registered_website):
        """Should set isPublished to False."""
        with flask_app.app_context():
            from app.models.website import WebsiteModel
            WebsiteModel.publish(registered_website['_id'])
            updated = WebsiteModel.unpublish(registered_website['_id'])
            assert updated['isPublished'] is False

    def test_add_page(self, flask_app, registered_website):
        """Should add a new page to the website."""
        with flask_app.app_context():
            from app.models.website import WebsiteModel
            page = WebsiteModel.add_page(registered_website['_id'], {
                'title': 'About',
                'slug': 'about',
                'content': {'text': 'About us'},
                'meta': {}
            })
            assert page is not None
            assert page['title'] == 'About'
            assert page['slug'] == 'about'

    def test_delete_website(self, flask_app, registered_website):
        """Should delete a website and return True."""
        with flask_app.app_context():
            from app.models.website import WebsiteModel
            deleted = WebsiteModel.delete_by_id(registered_website['_id'])
            assert deleted is True
            found = WebsiteModel.find_by_id(registered_website['_id'])
            assert found is None

    def test_count_by_user(self, flask_app, registered_user, registered_website):
        """Should correctly count websites for a user."""
        with flask_app.app_context():
            from app.models.website import WebsiteModel
            count = WebsiteModel.count_by_user(str(registered_user['_id']))
            assert count == 1

    def test_subdomain_exists(self, flask_app, registered_website):
        """Should return True when subdomain is taken."""
        with flask_app.app_context():
            from app.models.website import WebsiteModel
            exists = WebsiteModel.subdomain_exists(registered_website['subdomain'])
            assert exists is True

    def test_subdomain_not_exists(self, flask_app, clean_db):
        """Should return False for an unused subdomain."""
        with flask_app.app_context():
            from app.models.website import WebsiteModel
            exists = WebsiteModel.subdomain_exists('totally-unused-sub')
            assert exists is False


class TestSubscriptionModel:
    """Tests for SubscriptionModel."""

    def test_seed_and_find_plans(self, flask_app, clean_db):
        """Should seed default plans and find them."""
        with flask_app.app_context():
            from app.models.subscription import SubscriptionModel
            SubscriptionModel.seed_default_plans()
            plans = SubscriptionModel.find_all_active()
            assert len(plans) == 3
            names = [p['name'] for p in plans]
            assert 'basic' in names
            assert 'premium' in names
            assert 'enterprise' in names

    def test_find_by_name(self, flask_app, clean_db):
        """Should find a plan by name."""
        with flask_app.app_context():
            from app.models.subscription import SubscriptionModel
            SubscriptionModel.seed_default_plans()
            plan = SubscriptionModel.find_by_name('premium')
            assert plan is not None
            assert plan['price'] == 29.99
            assert plan['customDomain'] is True

    def test_find_by_name_not_found(self, flask_app, clean_db):
        """Should return None for an unknown plan name."""
        with flask_app.app_context():
            from app.models.subscription import SubscriptionModel
            plan = SubscriptionModel.find_by_name('nonexistent')
            assert plan is None