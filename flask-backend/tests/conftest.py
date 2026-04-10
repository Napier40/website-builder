"""
Pytest Configuration and Fixtures
Provides reusable test fixtures for all test modules.
Uses mongomock for in-memory MongoDB testing (no real DB needed).
"""
import pytest
import mongomock
from flask_jwt_extended import create_access_token

from app import create_app
import app.database as db_module


@pytest.fixture(scope='session')
def flask_app():
    """
    Create a Flask test application (session-scoped, created once per test run).
    Uses mongomock for an in-memory database.
    """
    application = create_app('testing')
    application.config.update({
        'TESTING': True,
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'STRIPE_SECRET_KEY': 'sk_test_fake_key',
        'WTF_CSRF_ENABLED': False
    })

    # Ensure mongomock is used
    mock_client = mongomock.MongoClient()
    application.db_client = mock_client
    application.db = mock_client['website-builder-test']
    db_module._client = mock_client
    db_module._db = application.db

    yield application


@pytest.fixture(scope='function')
def client(flask_app):
    """Provide a test client for HTTP requests."""
    with flask_app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope='function', autouse=True)
def clean_db(flask_app):
    """
    Clean all collections before each test function to ensure isolation.
    autouse=True means this runs automatically for every test.
    """
    db = flask_app.db
    for collection_name in db.list_collection_names():
        db[collection_name].drop()
    yield
    # Cleanup after test too
    for collection_name in db.list_collection_names():
        db[collection_name].drop()


@pytest.fixture
def app_context(flask_app):
    """Push the Flask app context."""
    with flask_app.app_context():
        yield flask_app


# ─── User Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def sample_user_data():
    """Raw data for creating a test user."""
    return {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'TestPassword123'
    }


@pytest.fixture
def sample_admin_data():
    """Raw data for creating a test admin."""
    return {
        'name': 'Test Admin',
        'email': 'testadmin@example.com',
        'password': 'AdminPassword123',
        'role': 'admin'
    }


@pytest.fixture
def registered_user(flask_app, sample_user_data):
    """A user registered directly in the database (bypassing HTTP)."""
    with flask_app.app_context():
        from app.models.user import UserModel
        user = UserModel.create(
            name=sample_user_data['name'],
            email=sample_user_data['email'],
            password=sample_user_data['password']
        )
        return user


@pytest.fixture
def registered_admin(flask_app, sample_admin_data):
    """An admin user registered directly in the database."""
    with flask_app.app_context():
        from app.models.user import UserModel
        admin = UserModel.create(
            name=sample_admin_data['name'],
            email=sample_admin_data['email'],
            password=sample_admin_data['password'],
            role='admin'
        )
        return admin


@pytest.fixture
def user_token(flask_app, registered_user):
    """A valid JWT token for the test user."""
    with flask_app.app_context():
        return create_access_token(identity=str(registered_user['_id']))


@pytest.fixture
def admin_token(flask_app, registered_admin):
    """A valid JWT token for the test admin."""
    with flask_app.app_context():
        return create_access_token(identity=str(registered_admin['_id']))


@pytest.fixture
def auth_headers(user_token):
    """HTTP Authorization headers with user JWT."""
    return {'Authorization': f'Bearer {user_token}', 'Content-Type': 'application/json'}


@pytest.fixture
def admin_headers(admin_token):
    """HTTP Authorization headers with admin JWT."""
    return {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}


# ─── Website Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def sample_website_data():
    """Raw data for creating a test website."""
    return {
        'name': 'Test Website',
        'subdomain': 'test-website-123',
        'template': 'default'
    }


@pytest.fixture
def registered_website(flask_app, registered_user, sample_website_data):
    """A website created directly in the database."""
    with flask_app.app_context():
        from app.models.website import WebsiteModel
        website = WebsiteModel.create(
            name=sample_website_data['name'],
            subdomain=sample_website_data['subdomain'],
            user_id=str(registered_user['_id']),
            template=sample_website_data['template']
        )
        return website