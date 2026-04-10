"""
pytest fixtures — uses an in-memory SQLite database (no external DB needed)
"""
import pytest
from app import create_app
from app.database import db as _db


@pytest.fixture(scope='session')
def flask_app():
    """Create the Flask app once per test session using in-memory SQLite."""
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def client(flask_app):
    """Test client with a fresh database for each test function."""
    with flask_app.app_context():
        _db.create_all()
        yield flask_app.test_client()
        _db.session.remove()
        _db.drop_all()


# ── Seed helpers ──────────────────────────────────────────────────────────────

@pytest.fixture
def registered_user(client, flask_app):
    """Register and return a standard user."""
    with flask_app.app_context():
        from app.models.user import User
        user = User.create(name='Test User', email='test@example.com', password='password123')
        return {'id': user.id, 'email': user.email, 'password': 'password123'}


@pytest.fixture
def registered_admin(client, flask_app):
    """Register and return an admin user."""
    with flask_app.app_context():
        from app.models.user import User
        admin = User.create(name='Admin User', email='admin@example.com',
                            password='adminpass123', role='admin')
        return {'id': admin.id, 'email': admin.email, 'password': 'adminpass123'}


@pytest.fixture
def user_token(client, registered_user):
    """JWT token for the standard user."""
    resp = client.post('/api/auth/login', json={
        'email':    registered_user['email'],
        'password': registered_user['password'],
    })
    assert resp.status_code == 200
    return resp.get_json()['data']['token']


@pytest.fixture
def admin_token(client, registered_admin):
    """JWT token for the admin user."""
    resp = client.post('/api/auth/login', json={
        'email':    registered_admin['email'],
        'password': registered_admin['password'],
    })
    assert resp.status_code == 200
    return resp.get_json()['data']['token']


@pytest.fixture
def auth_headers(user_token):
    return {'Authorization': f'Bearer {user_token}'}


@pytest.fixture
def admin_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}'}


@pytest.fixture
def registered_website(client, flask_app, auth_headers, registered_user):
    """Create and return a website owned by the standard user."""
    resp = client.post('/api/websites/', json={
        'name':      'Test Website',
        'subdomain': 'test-site',
        'template':  'blank',
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.get_json()['data']['website']