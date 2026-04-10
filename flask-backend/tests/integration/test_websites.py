"""
Integration Tests - Websites API
Tests all /api/websites/* endpoints end-to-end
"""
import pytest


class TestGetMyWebsites:
    """Tests for GET /api/websites"""

    def test_get_my_websites_empty(self, client, auth_headers):
        """Should return empty list when user has no websites."""
        response = client.get('/api/websites', headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['count'] == 0
        assert data['websites'] == []

    def test_get_my_websites_with_data(self, client, auth_headers, registered_website):
        """Should return websites belonging to the current user."""
        response = client.get('/api/websites', headers=auth_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['count'] == 1
        assert data['websites'][0]['name'] == 'Test Website'

    def test_get_my_websites_unauthorized(self, client):
        """Should return 401 without authentication."""
        response = client.get('/api/websites')
        assert response.status_code == 401


class TestCreateWebsite:
    """Tests for POST /api/websites"""

    def test_create_website_success(self, client, auth_headers, clean_db, registered_user):
        """Should create a new website with default home page."""
        # Register the user fixture first
        response = client.post(
            '/api/websites',
            json={'name': 'My New Site', 'subdomain': 'my-new-site-xyz'},
            headers=auth_headers
        )
        data = response.get_json()

        assert response.status_code == 201
        assert data['success'] is True
        assert data['website']['name'] == 'My New Site'
        assert data['website']['subdomain'] == 'my-new-site-xyz'
        assert data['website']['isPublished'] is False
        assert len(data['website']['pages']) == 1

    def test_create_website_missing_name(self, client, auth_headers):
        """Should return 400 when name is missing."""
        response = client.post(
            '/api/websites',
            json={'subdomain': 'valid-sub'},
            headers=auth_headers
        )
        assert response.status_code == 400

    def test_create_website_missing_subdomain(self, client, auth_headers):
        """Should return 400 when subdomain is missing."""
        response = client.post(
            '/api/websites',
            json={'name': 'My Site'},
            headers=auth_headers
        )
        assert response.status_code == 400

    def test_create_website_invalid_subdomain(self, client, auth_headers):
        """Should return 400 for invalid subdomain format."""
        response = client.post(
            '/api/websites',
            json={'name': 'My Site', 'subdomain': 'AB'},  # too short / uppercase
            headers=auth_headers
        )
        assert response.status_code == 400

    def test_create_website_duplicate_subdomain(self, client, admin_headers, registered_admin,
                                                    registered_website):
        """
        Should return 400 for a duplicate subdomain.
        Uses admin user (no website limit) to isolate the subdomain check.
        """
        # Admin has no website limit, so we'll test subdomain conflict directly
        # First create a site as admin with the same subdomain
        response = client.post(
            '/api/websites',
            json={'name': 'Another Site', 'subdomain': 'test-website-123'},
            headers=admin_headers
        )
        # The subdomain 'test-website-123' already belongs to registered_website (owned by regular user)
        assert response.status_code == 400

    def test_create_website_unauthorized(self, client):
        """Should return 401 without token."""
        response = client.post('/api/websites', json={'name': 'Site', 'subdomain': 'site'})
        assert response.status_code == 401


class TestGetWebsiteById:
    """Tests for GET /api/websites/<id>"""

    def test_get_website_by_id_success(self, client, auth_headers, registered_website):
        """Should return website by ID."""
        response = client.get(
            f"/api/websites/{registered_website['_id']}",
            headers=auth_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['website']['_id'] == registered_website['_id']

    def test_get_website_not_found(self, client, auth_headers):
        """Should return 404 for non-existent website."""
        from bson import ObjectId
        fake_id = str(ObjectId())
        response = client.get(f'/api/websites/{fake_id}', headers=auth_headers)
        assert response.status_code == 404

    def test_get_website_invalid_id(self, client, auth_headers):
        """Should return 400 for invalid ObjectId format."""
        response = client.get('/api/websites/not-a-valid-id', headers=auth_headers)
        assert response.status_code == 400

    def test_get_website_wrong_user(self, client, registered_website, registered_admin, admin_token):
        """Admin should be able to access any website."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.get(
            f"/api/websites/{registered_website['_id']}",
            headers=headers
        )
        # Admin can access any website
        assert response.status_code == 200


class TestUpdateWebsite:
    """Tests for PUT /api/websites/<id>"""

    def test_update_website_name(self, client, auth_headers, registered_website):
        """Should update website name."""
        response = client.put(
            f"/api/websites/{registered_website['_id']}",
            json={'name': 'Updated Name'},
            headers=auth_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['website']['name'] == 'Updated Name'

    def test_update_website_settings(self, client, auth_headers, registered_website):
        """Should merge-update website settings."""
        new_settings = {
            'theme': {
                'primaryColor': '#ff0000',
                'secondaryColor': '#00ff00'
            }
        }
        response = client.put(
            f"/api/websites/{registered_website['_id']}",
            json={'settings': new_settings},
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_update_website_unauthorized(self, client, registered_website):
        """Should return 401 without token."""
        response = client.put(
            f"/api/websites/{registered_website['_id']}",
            json={'name': 'Hacked'}
        )
        assert response.status_code == 401


class TestPublishUnpublish:
    """Tests for PUT /api/websites/<id>/publish and /unpublish"""

    def test_publish_website(self, client, auth_headers, registered_website):
        """Should publish a website."""
        response = client.put(
            f"/api/websites/{registered_website['_id']}/publish",
            headers=auth_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['website']['isPublished'] is True

    def test_unpublish_website(self, client, auth_headers, registered_website):
        """Should unpublish a website."""
        # First publish it
        client.put(
            f"/api/websites/{registered_website['_id']}/publish",
            headers=auth_headers
        )
        # Then unpublish
        response = client.put(
            f"/api/websites/{registered_website['_id']}/unpublish",
            headers=auth_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        assert data['website']['isPublished'] is False


class TestPageManagement:
    """Tests for page CRUD within a website."""

    def test_create_page(self, client, auth_headers, registered_website):
        """Should add a new page to the website."""
        response = client.post(
            f"/api/websites/{registered_website['_id']}/pages",
            json={'title': 'About', 'slug': 'about'},
            headers=auth_headers
        )
        data = response.get_json()

        assert response.status_code == 201
        assert data['success'] is True
        assert data['page']['title'] == 'About'
        assert data['page']['slug'] == 'about'

    def test_create_page_duplicate_slug(self, client, auth_headers, registered_website):
        """Should return 400 for duplicate slug."""
        # 'home' already exists
        response = client.post(
            f"/api/websites/{registered_website['_id']}/pages",
            json={'title': 'Home2', 'slug': 'home'},
            headers=auth_headers
        )
        assert response.status_code == 400

    def test_delete_home_page_forbidden(self, client, auth_headers, registered_website):
        """Should return 400 when trying to delete home page."""
        website = registered_website
        home_page_id = website['pages'][0]['_id']

        response = client.delete(
            f"/api/websites/{registered_website['_id']}/pages/{home_page_id}",
            headers=auth_headers
        )
        assert response.status_code == 400


class TestDeleteWebsite:
    """Tests for DELETE /api/websites/<id>"""

    def test_delete_website_success(self, client, auth_headers, registered_website):
        """Should delete a website successfully."""
        response = client.delete(
            f"/api/websites/{registered_website['_id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.get_json()['success'] is True

    def test_delete_website_not_found(self, client, auth_headers):
        """Should return 404 for a non-existent website."""
        from bson import ObjectId
        fake_id = str(ObjectId())
        response = client.delete(f'/api/websites/{fake_id}', headers=auth_headers)
        assert response.status_code == 404

    def test_delete_website_unauthorized(self, client, registered_website):
        """Should return 401 without token."""
        response = client.delete(f"/api/websites/{registered_website['_id']}")
        assert response.status_code == 401