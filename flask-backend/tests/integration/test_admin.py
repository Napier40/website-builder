"""
Integration Tests - Admin API
Tests all /api/admin/* endpoints
"""
import pytest
from bson import ObjectId


class TestAdminDashboard:
    """Tests for GET /api/admin/dashboard"""

    def test_dashboard_admin_access(self, client, admin_headers):
        """Admin should be able to access dashboard."""
        response = client.get('/api/admin/dashboard', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert 'data' in data
        assert 'users' in data['data']
        assert 'websites' in data['data']
        assert 'revenue' in data['data']

    def test_dashboard_user_forbidden(self, client, auth_headers):
        """Regular user should not be able to access admin dashboard."""
        response = client.get('/api/admin/dashboard', headers=auth_headers)
        assert response.status_code == 403

    def test_dashboard_unauthenticated(self, client):
        """Unauthenticated request should return 401."""
        response = client.get('/api/admin/dashboard')
        assert response.status_code == 401


class TestAdminUserManagement:
    """Tests for /api/admin/users endpoints"""

    def test_get_all_users(self, client, admin_headers, registered_user):
        """Admin should retrieve all users."""
        response = client.get('/api/admin/users', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['total'] >= 1

    def test_get_all_users_with_search(self, client, admin_headers, registered_user):
        """Admin should be able to search users."""
        response = client.get(
            '/api/admin/users?search=testuser',
            headers=admin_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['total'] >= 1

    def test_get_user_by_id(self, client, admin_headers, registered_user):
        """Admin should get full user profile."""
        response = client.get(
            f"/api/admin/users/{registered_user['_id']}",
            headers=admin_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['user']['_id'] == registered_user['_id']
        assert 'websites' in data['data']
        assert 'payments' in data['data']
        assert 'auditLogs' in data['data']

    def test_update_user_role(self, client, admin_headers, registered_user):
        """Admin should be able to change a user's role."""
        response = client.put(
            f"/api/admin/users/{registered_user['_id']}",
            json={'role': 'admin'},
            headers=admin_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['role'] == 'admin'

    def test_update_user_subscription(self, client, admin_headers, registered_user):
        """Admin should be able to update subscription status."""
        response = client.put(
            f"/api/admin/users/{registered_user['_id']}",
            json={'subscriptionStatus': 'premium'},
            headers=admin_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['subscriptionStatus'] == 'premium'

    def test_get_user_invalid_id(self, client, admin_headers):
        """Should return 400 for invalid ObjectId."""
        response = client.get('/api/admin/users/invalid-id', headers=admin_headers)
        assert response.status_code == 400

    def test_get_user_not_found(self, client, admin_headers):
        """Should return 404 for non-existent user."""
        fake_id = str(ObjectId())
        response = client.get(f'/api/admin/users/{fake_id}', headers=admin_headers)
        assert response.status_code == 404

    def test_regular_user_cannot_access_admin_users(self, client, auth_headers):
        """Regular user should get 403."""
        response = client.get('/api/admin/users', headers=auth_headers)
        assert response.status_code == 403


class TestAdminModeration:
    """Tests for /api/admin/moderation endpoints"""

    def test_get_moderation_queue(self, client, admin_headers):
        """Admin should get the moderation queue."""
        response = client.get('/api/admin/moderation', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert 'data' in data

    def test_flag_content_for_moderation(self, client, admin_headers, registered_website):
        """Admin should be able to flag content."""
        response = client.post(
            '/api/admin/moderation',
            json={
                'contentId': registered_website['_id'],
                'contentModel': 'Website',
                'reason': 'Contains inappropriate content'
            },
            headers=admin_headers
        )
        data = response.get_json()

        assert response.status_code == 201
        assert data['success'] is True
        assert data['data']['status'] == 'pending'

    def test_process_moderation_approve(self, client, admin_headers, registered_website):
        """Admin should approve a moderation item."""
        # First flag the content
        flag_resp = client.post(
            '/api/admin/moderation',
            json={
                'contentId': registered_website['_id'],
                'contentModel': 'Website',
                'reason': 'Test flagging'
            },
            headers=admin_headers
        )
        mod_id = flag_resp.get_json()['data']['_id']

        # Then approve it
        response = client.put(
            f'/api/admin/moderation/{mod_id}',
            json={'status': 'approved', 'reason': 'Content is fine', 'action': 'no_action'},
            headers=admin_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['status'] == 'approved'

    def test_flag_content_missing_fields(self, client, admin_headers):
        """Should return 400 when required fields are missing."""
        response = client.post(
            '/api/admin/moderation',
            json={'reason': 'Some reason'},
            headers=admin_headers
        )
        assert response.status_code == 400


class TestAdminContentOverride:
    """Tests for PUT /api/admin/websites/<id>/override"""

    def test_override_website_content(self, client, admin_headers, registered_website):
        """Admin should be able to override website content."""
        new_pages = [
            {
                'title': 'Admin Override Page',
                'slug': 'home',
                'content': {'sections': []},
                'isPublished': True,
                'meta': {}
            }
        ]

        response = client.put(
            f"/api/admin/websites/{registered_website['_id']}/override",
            json={'content': new_pages, 'reason': 'Removing inappropriate content'},
            headers=admin_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['adminOverride']['reason'] == 'Removing inappropriate content'

    def test_override_requires_content(self, client, admin_headers, registered_website):
        """Should return 400 when content is missing."""
        response = client.put(
            f"/api/admin/websites/{registered_website['_id']}/override",
            json={'reason': 'Some reason'},
            headers=admin_headers
        )
        assert response.status_code == 400

    def test_regular_user_cannot_override(self, client, auth_headers, registered_website):
        """Regular user cannot override website content."""
        response = client.put(
            f"/api/admin/websites/{registered_website['_id']}/override",
            json={'content': [], 'reason': 'Attempt'},
            headers=auth_headers
        )
        assert response.status_code == 403


class TestAuditLogs:
    """Tests for GET /api/admin/audit-logs"""

    def test_get_audit_logs(self, client, admin_headers):
        """Admin should retrieve audit logs."""
        response = client.get('/api/admin/audit-logs', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True

    def test_audit_logs_with_action_filter(self, client, admin_headers):
        """Should filter audit logs by action."""
        response = client.get(
            '/api/admin/audit-logs?action=LOGIN',
            headers=admin_headers
        )
        assert response.status_code == 200

    def test_regular_user_cannot_access_audit_logs(self, client, auth_headers):
        """Regular user should get 403."""
        response = client.get('/api/admin/audit-logs', headers=auth_headers)
        assert response.status_code == 403