"""
Integration tests — Auth endpoints
"""
import pytest


class TestRegister:

    def test_register_success(self, client):
        resp = client.post('/api/auth/register', json={
            'name': 'New User', 'email': 'new@example.com', 'password': 'password123'
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['success'] is True
        assert 'token' in data['data']
        assert data['data']['user']['email'] == 'new@example.com'

    def test_register_duplicate_email(self, client):
        payload = {'name': 'User', 'email': 'dup@example.com', 'password': 'password123'}
        client.post('/api/auth/register', json=payload)
        resp = client.post('/api/auth/register', json=payload)
        assert resp.status_code == 409

    def test_register_missing_name(self, client):
        resp = client.post('/api/auth/register', json={
            'email': 'x@example.com', 'password': 'password123'
        })
        assert resp.status_code == 400

    def test_register_missing_email(self, client):
        resp = client.post('/api/auth/register', json={
            'name': 'X', 'password': 'password123'
        })
        assert resp.status_code == 400

    def test_register_missing_password(self, client):
        resp = client.post('/api/auth/register', json={
            'name': 'X', 'email': 'x@example.com'
        })
        assert resp.status_code == 400

    def test_register_invalid_email(self, client):
        resp = client.post('/api/auth/register', json={
            'name': 'X', 'email': 'not-an-email', 'password': 'password123'
        })
        assert resp.status_code == 400

    def test_register_short_password(self, client):
        resp = client.post('/api/auth/register', json={
            'name': 'X', 'email': 'x@example.com', 'password': '123'
        })
        assert resp.status_code == 400

    def test_register_no_body(self, client):
        resp = client.post('/api/auth/register')
        assert resp.status_code in (400, 415)


class TestLogin:

    def test_login_success(self, client, registered_user):
        resp = client.post('/api/auth/login', json={
            'email': registered_user['email'], 'password': registered_user['password']
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'token' in data['data']

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post('/api/auth/login', json={
            'email': registered_user['email'], 'password': 'wrongpassword'
        })
        assert resp.status_code == 401

    def test_login_unknown_email(self, client):
        resp = client.post('/api/auth/login', json={
            'email': 'nobody@example.com', 'password': 'password123'
        })
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        resp = client.post('/api/auth/login', json={'email': 'x@example.com'})
        assert resp.status_code == 400

    def test_login_no_body(self, client):
        resp = client.post('/api/auth/login')
        assert resp.status_code in (400, 415)


class TestProfile:

    def test_get_me(self, client, auth_headers):
        resp = client.get('/api/auth/me', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['user']['email'] == 'test@example.com'

    def test_get_me_no_token(self, client):
        resp = client.get('/api/auth/me')
        assert resp.status_code == 401

    def test_update_profile(self, client, auth_headers):
        resp = client.put('/api/auth/profile', json={'name': 'Updated Name'},
                          headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['user']['name'] == 'Updated Name'

    def test_change_password(self, client, auth_headers):
        resp = client.put('/api/auth/change-password', json={
            'currentPassword': 'password123',
            'newPassword':     'newpassword456',
        }, headers=auth_headers)
        assert resp.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        resp = client.put('/api/auth/change-password', json={
            'currentPassword': 'wrongpassword',
            'newPassword':     'newpassword456',
        }, headers=auth_headers)
        assert resp.status_code == 401


class TestHealthCheck:

    def test_health_check(self, client):
        resp = client.get('/api/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['database']['engine'] == 'SQLite'