"""
Integration tests — Admin endpoints
"""
import pytest


class TestDashboard:

    def test_dashboard_admin(self, client, admin_headers):
        resp = client.get('/api/admin/dashboard', headers=admin_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'stats' in data['data']
        assert 'totalUsers' in data['data']['stats']

    def test_dashboard_user_denied(self, client, auth_headers):
        resp = client.get('/api/admin/dashboard', headers=auth_headers)
        assert resp.status_code == 403

    def test_dashboard_no_auth(self, client):
        resp = client.get('/api/admin/dashboard')
        assert resp.status_code == 401


class TestAdminUsers:

    def test_get_all_users(self, client, admin_headers, registered_user):
        resp = client.get('/api/admin/users', headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['total'] >= 1

    def test_get_user_by_id(self, client, admin_headers, registered_user):
        uid  = registered_user['id']
        resp = client.get(f'/api/admin/users/{uid}', headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['user']['id'] == uid

    def test_get_user_not_found(self, client, admin_headers):
        resp = client.get('/api/admin/users/99999', headers=admin_headers)
        assert resp.status_code == 404

    def test_update_user(self, client, admin_headers, registered_user):
        uid  = registered_user['id']
        resp = client.put(f'/api/admin/users/{uid}',
                          json={'subscription_type': 'premium'},
                          headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['user']['subscriptionType'] == 'premium'

    def test_delete_user(self, client, admin_headers, registered_user):
        uid  = registered_user['id']
        resp = client.delete(f'/api/admin/users/{uid}', headers=admin_headers)
        assert resp.status_code == 200
        # Confirm gone
        resp2 = client.get(f'/api/admin/users/{uid}', headers=admin_headers)
        assert resp2.status_code == 404

    def test_cannot_delete_self(self, client, admin_headers, registered_admin):
        uid  = registered_admin['id']
        resp = client.delete(f'/api/admin/users/{uid}', headers=admin_headers)
        assert resp.status_code == 400

    def test_regular_user_cannot_access(self, client, auth_headers):
        resp = client.get('/api/admin/users', headers=auth_headers)
        assert resp.status_code == 403


class TestModeration:

    def test_create_moderation_report(self, client, auth_headers, registered_website):
        resp = client.post('/api/admin/moderation', json={
            'contentId':    str(registered_website['id']),
            'contentModel': 'Website',
            'reason':       'Inappropriate content',
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.get_json()['data']['moderation']['status'] == 'pending'

    def test_get_moderation_queue(self, client, admin_headers):
        resp = client.get('/api/admin/moderation', headers=admin_headers)
        assert resp.status_code == 200

    def test_review_moderation(self, client, admin_headers, auth_headers,
                               registered_website):
        # Create a report first
        create_resp = client.post('/api/admin/moderation', json={
            'contentId':    str(registered_website['id']),
            'contentModel': 'Website',
            'reason':       'Test report',
        }, headers=auth_headers)
        mid = create_resp.get_json()['data']['moderation']['id']

        # Admin reviews it
        resp = client.put(f'/api/admin/moderation/{mid}', json={
            'status': 'approved', 'notes': 'Looks fine'
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['moderation']['status'] == 'approved'

    def test_review_invalid_status(self, client, admin_headers, auth_headers,
                                   registered_website):
        create_resp = client.post('/api/admin/moderation', json={
            'contentId': str(registered_website['id']),
            'contentModel': 'Website',
            'reason': 'Test',
        }, headers=auth_headers)
        mid = create_resp.get_json()['data']['moderation']['id']
        resp = client.put(f'/api/admin/moderation/{mid}',
                          json={'status': 'invalid_status'},
                          headers=admin_headers)
        assert resp.status_code == 400


class TestWebsiteOverride:

    def test_admin_override(self, client, admin_headers, registered_website):
        wid  = registered_website['id']
        resp = client.put(f'/api/admin/websites/{wid}/override',
                          json={'reason': 'Admin review passed'},
                          headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['website']['moderationStatus'] == 'approved'

    def test_delete_website_content(self, client, admin_headers, registered_website):
        wid  = registered_website['id']
        resp = client.delete(f'/api/admin/websites/{wid}/delete-content',
                             headers=admin_headers)
        assert resp.status_code == 200


class TestAuditLogs:

    def test_get_audit_logs(self, client, admin_headers, registered_user):
        resp = client.get('/api/admin/audit-logs', headers=admin_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'data' in data

    def test_audit_logs_user_denied(self, client, auth_headers):
        resp = client.get('/api/admin/audit-logs', headers=auth_headers)
        assert resp.status_code == 403