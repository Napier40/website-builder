"""
Integration tests — Websites endpoints
"""
import pytest


class TestCreateWebsite:

    def test_create_website_success(self, client, auth_headers):
        resp = client.post('/api/websites/', json={
            'name': 'My Site', 'subdomain': 'my-site'
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['success'] is True
        assert data['data']['website']['subdomain'] == 'my-site'
        assert len(data['data']['website']['pages']) == 1

    def test_create_website_no_auth(self, client):
        resp = client.post('/api/websites/', json={
            'name': 'My Site', 'subdomain': 'no-auth'
        })
        assert resp.status_code == 401

    def test_create_website_missing_fields(self, client, auth_headers):
        resp = client.post('/api/websites/', json={'name': 'No Subdomain'},
                           headers=auth_headers)
        assert resp.status_code == 400

    def test_create_website_invalid_subdomain(self, client, auth_headers):
        resp = client.post('/api/websites/', json={
            'name': 'Bad Sub', 'subdomain': 'AB'   # too short / uppercase
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_create_website_duplicate_subdomain(self, client, admin_headers):
        client.post('/api/websites/', json={
            'name': 'Site 1', 'subdomain': 'dupe-sub'
        }, headers=admin_headers)
        resp = client.post('/api/websites/', json={
            'name': 'Site 2', 'subdomain': 'dupe-sub'
        }, headers=admin_headers)
        assert resp.status_code == 409

    def test_free_user_website_limit(self, client, auth_headers, registered_website):
        # Free user already has 1 website; limit is 1
        resp = client.post('/api/websites/', json={
            'name': 'Second Site', 'subdomain': 'second-site'
        }, headers=auth_headers)
        assert resp.status_code == 403


class TestGetWebsite:

    def test_get_my_websites(self, client, auth_headers, registered_website):
        resp = client.get('/api/websites/', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['total'] >= 1

    def test_get_website_by_id(self, client, auth_headers, registered_website):
        wid  = registered_website['id']
        resp = client.get(f'/api/websites/{wid}', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['website']['id'] == wid

    def test_get_website_not_found(self, client, auth_headers):
        resp = client.get('/api/websites/99999', headers=auth_headers)
        assert resp.status_code == 404

    def test_get_website_other_user_denied(self, client, registered_website,
                                           flask_app):
        with flask_app.app_context():
            from app.models.user import User
            other = User.create(name='Other', email='other@example.com', password='pass123')
        resp_login = client.post('/api/auth/login', json={
            'email': 'other@example.com', 'password': 'pass123'
        })
        other_token = resp_login.get_json()['data']['token']
        wid  = registered_website['id']
        resp = client.get(f'/api/websites/{wid}',
                          headers={'Authorization': f'Bearer {other_token}'})
        assert resp.status_code == 403


class TestUpdateWebsite:

    def test_update_website(self, client, auth_headers, registered_website):
        wid  = registered_website['id']
        resp = client.put(f'/api/websites/{wid}', json={'name': 'Renamed'},
                          headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['website']['name'] == 'Renamed'

    def test_update_website_no_auth(self, client, registered_website):
        wid  = registered_website['id']
        resp = client.put(f'/api/websites/{wid}', json={'name': 'X'})
        assert resp.status_code == 401


class TestPublishWebsite:

    def test_publish(self, client, auth_headers, registered_website):
        wid  = registered_website['id']
        resp = client.put(f'/api/websites/{wid}/publish', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['website']['isPublished'] is True

    def test_unpublish(self, client, auth_headers, registered_website):
        wid  = registered_website['id']
        client.put(f'/api/websites/{wid}/publish', headers=auth_headers)
        resp = client.put(f'/api/websites/{wid}/unpublish', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['website']['isPublished'] is False


class TestPages:

    def test_add_page(self, client, auth_headers, registered_website):
        wid  = registered_website['id']
        resp = client.post(f'/api/websites/{wid}/pages', json={
            'title': 'About', 'slug': 'about', 'content': '<p>About us</p>'
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.get_json()['data']['page']['slug'] == 'about'

    def test_update_page(self, client, auth_headers, registered_website):
        wid = registered_website['id']
        pid = registered_website['pages'][0]['id']
        resp = client.put(f'/api/websites/{wid}/pages/{pid}',
                          json={'title': 'Home Updated'},
                          headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['data']['page']['title'] == 'Home Updated'

    def test_delete_page(self, client, auth_headers, registered_website):
        wid = registered_website['id']
        pid = registered_website['pages'][0]['id']
        resp = client.delete(f'/api/websites/{wid}/pages/{pid}',
                             headers=auth_headers)
        assert resp.status_code == 200


class TestDeleteWebsite:

    def test_delete_website(self, client, auth_headers, registered_website):
        wid  = registered_website['id']
        resp = client.delete(f'/api/websites/{wid}', headers=auth_headers)
        assert resp.status_code == 200
        # Confirm gone
        resp2 = client.get(f'/api/websites/{wid}', headers=auth_headers)
        assert resp2.status_code == 404