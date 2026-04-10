"""
Integration Tests - Authentication API
Tests all /api/auth/* endpoints end-to-end
"""
import json
import pytest


class TestRegister:
    """Integration tests for POST /api/auth/register"""

    def test_register_success(self, client, clean_db):
        """Should register a new user and return token."""
        response = client.post(
            '/api/auth/register',
            json={'name': 'John Doe', 'email': 'john@example.com', 'password': 'Password123'}
        )
        data = response.get_json()

        assert response.status_code == 201
        assert data['success'] is True
        assert 'token' in data
        assert 'user' in data
        assert data['user']['email'] == 'john@example.com'
        assert 'password' not in data['user']

    def test_register_missing_name(self, client, clean_db):
        """Should return 400 when name is missing."""
        response = client.post(
            '/api/auth/register',
            json={'email': 'john@example.com', 'password': 'Password123'}
        )
        assert response.status_code == 400
        assert response.get_json()['success'] is False

    def test_register_missing_email(self, client, clean_db):
        """Should return 400 when email is missing."""
        response = client.post(
            '/api/auth/register',
            json={'name': 'John', 'password': 'Password123'}
        )
        assert response.status_code == 400

    def test_register_missing_password(self, client, clean_db):
        """Should return 400 when password is missing."""
        response = client.post(
            '/api/auth/register',
            json={'name': 'John', 'email': 'john@example.com'}
        )
        assert response.status_code == 400

    def test_register_invalid_email(self, client, clean_db):
        """Should return 400 for an invalid email format."""
        response = client.post(
            '/api/auth/register',
            json={'name': 'John', 'email': 'not-an-email', 'password': 'Password123'}
        )
        assert response.status_code == 400

    def test_register_short_password(self, client, clean_db):
        """Should return 400 for password shorter than 6 characters."""
        response = client.post(
            '/api/auth/register',
            json={'name': 'John', 'email': 'john@example.com', 'password': '123'}
        )
        assert response.status_code == 400

    def test_register_duplicate_email(self, client, registered_user, clean_db):
        """Should return 400 when email already exists."""
        response = client.post(
            '/api/auth/register',
            json={
                'name': 'Another User',
                'email': 'testuser@example.com',  # same as registered_user
                'password': 'Password123'
            }
        )
        assert response.status_code == 400
        assert 'already exists' in response.get_json()['message'].lower()

    def test_register_no_json_body(self, client, clean_db):
        """Should return 400 or 415 when no JSON body is provided."""
        response = client.post('/api/auth/register')
        assert response.status_code in (400, 415)  # Flask returns 415 for missing Content-Type


class TestLogin:
    """Integration tests for POST /api/auth/login"""

    def test_login_success(self, client, registered_user):
        """Should login successfully and return JWT token."""
        response = client.post(
            '/api/auth/login',
            json={'email': 'testuser@example.com', 'password': 'TestPassword123'}
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert 'token' in data
        assert data['user']['email'] == 'testuser@example.com'
        assert 'password' not in data['user']

    def test_login_wrong_password(self, client, registered_user):
        """Should return 401 for incorrect password."""
        response = client.post(
            '/api/auth/login',
            json={'email': 'testuser@example.com', 'password': 'WrongPassword'}
        )
        assert response.status_code == 401
        assert response.get_json()['success'] is False

    def test_login_unknown_email(self, client, clean_db):
        """Should return 401 for unknown email."""
        response = client.post(
            '/api/auth/login',
            json={'email': 'nobody@example.com', 'password': 'Password123'}
        )
        assert response.status_code == 401

    def test_login_missing_fields(self, client, clean_db):
        """Should return 400 when fields are missing."""
        response = client.post('/api/auth/login', json={'email': 'test@example.com'})
        assert response.status_code == 400

    def test_login_no_json_body(self, client, clean_db):
        """Should return 400 or 415 when no body provided."""
        response = client.post('/api/auth/login')
        assert response.status_code in (400, 415)  # Flask returns 415 for missing Content-Type


class TestGetMe:
    """Integration tests for GET /api/auth/me"""

    def test_get_me_success(self, client, auth_headers):
        """Should return current user's profile."""
        response = client.get('/api/auth/me', headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['email'] == 'testuser@example.com'

    def test_get_me_no_token(self, client):
        """Should return 401 without a token."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        """Should return 401 with an invalid token."""
        headers = {'Authorization': 'Bearer invalid.token.here'}
        response = client.get('/api/auth/me', headers=headers)
        assert response.status_code == 401


class TestUpdateProfile:
    """Integration tests for PUT /api/auth/profile"""

    def test_update_name(self, client, auth_headers):
        """Should update the user's name."""
        response = client.put(
            '/api/auth/profile',
            json={'name': 'Updated Name'},
            headers=auth_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['user']['name'] == 'Updated Name'

    def test_update_email(self, client, auth_headers):
        """Should update the user's email."""
        response = client.put(
            '/api/auth/profile',
            json={'email': 'newemail@example.com'},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.get_json()['user']['email'] == 'newemail@example.com'

    def test_update_invalid_email(self, client, auth_headers):
        """Should return 400 for invalid email."""
        response = client.put(
            '/api/auth/profile',
            json={'email': 'not-an-email'},
            headers=auth_headers
        )
        assert response.status_code == 400

    def test_update_profile_unauthorized(self, client):
        """Should return 401 without token."""
        response = client.put('/api/auth/profile', json={'name': 'Hacker'})
        assert response.status_code == 401


class TestChangePassword:
    """Integration tests for PUT /api/auth/change-password"""

    def test_change_password_success(self, client, auth_headers):
        """Should change password when current password is correct."""
        response = client.put(
            '/api/auth/change-password',
            json={
                'currentPassword': 'TestPassword123',
                'newPassword': 'NewSecurePass456'
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.get_json()['success'] is True

    def test_change_password_wrong_current(self, client, auth_headers):
        """Should return 401 when current password is wrong."""
        response = client.put(
            '/api/auth/change-password',
            json={
                'currentPassword': 'WrongCurrentPassword',
                'newPassword': 'NewPass123'
            },
            headers=auth_headers
        )
        assert response.status_code == 401

    def test_change_password_weak_new(self, client, auth_headers):
        """Should return 400 when new password is too short."""
        response = client.put(
            '/api/auth/change-password',
            json={
                'currentPassword': 'TestPassword123',
                'newPassword': '123'
            },
            headers=auth_headers
        )
        assert response.status_code == 400