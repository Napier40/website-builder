"""
Integration tests for templates and translations endpoints.
"""
import pytest


class TestTranslationsEndpoints:
    """Test the translations API endpoints."""

    @pytest.fixture(autouse=True)
    def setup_translations(self, seeded_translations):
        """Autouse fixture to seed translations before tests."""
        pass
    """Test the translations API endpoints."""

    def test_get_translations_all_namespaces(self, client):
        """Test getting all translations grouped by namespace."""
        resp = client.get('/api/i18n/?language=en')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'translations' in data['data']
        assert 'language' in data['data']
        assert data['data']['language'] == 'en'

        # Verify some namespaces exist
        translations = data['data']['translations']
        assert 'common' in translations
        assert 'builder' in translations
        assert 'auth' in translations

        # Verify some common translations
        assert 'save' in translations['common']
        assert 'delete' in translations['common']

    def test_get_translations_namespace(self, client):
        """Test getting translations for a specific namespace."""
        resp = client.get('/api/i18n/?language=en&namespace=builder')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'translations' in data['data']
        assert data['data']['namespace'] == 'builder'

        # Verify builder-specific translations
        translations = data['data']['translations']
        assert 'pageTitle' in translations
        assert 'dragToCanvas' in translations
        assert 'saveSuccess' in translations

    def test_get_translations_fallback_to_english(self, client):
        """Test that missing translations fall back to English."""
        # Request a non-existent language with a specific namespace
        resp = client.get('/api/i18n/?language=fr&namespace=common')
        assert resp.status_code == 200
        data = resp.get_json()

        # Should fall back to English
        assert data['data']['language'] == 'fr'  # Requested language in response
        assert data['data']['namespace'] == 'common'
        assert data['data']['translations'] is not None  # But still get English data

        # Verify we get English data
        assert 'save' in data['data']['translations']

    def test_get_translation_single_key(self, client):
        """Test getting a single translation by key."""
        resp = client.get('/api/i18n/keys/save?language=en')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['data']['key'] == 'save'
        assert data['data']['language'] == 'en'
        assert data['data']['value'] is not None

    def test_get_translation_not_found(self, client):
        """Test getting a non-existent translation key."""
        resp = client.get('/api/i18n/keys/nonexistent_key_12345?language=en')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['success'] is False
        assert 'not found' in data['message'].lower()

    def test_get_translations_languages(self, client):
        """Test getting list of supported languages."""
        resp = client.get('/api/i18n/languages')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'languages' in data['data']

        # English should always be available
        languages = data['data']['languages']
        assert 'en' in languages

    def test_create_translation_admin_only(self, client, user_token):
        """Test that creating a translation requires admin role."""
        # Regular user should be denied
        resp = client.post('/api/i18n/',
                           json={'key': 'test_key', 'language': 'en', 'value': 'Test value'},
                           headers={'Authorization': f'Bearer {user_token}'})
        assert resp.status_code == 403  # Forbidden - not admin

    def test_create_translation_invalid_data(self, client, admin_headers):
        """Test creating a translation with invalid data."""
        # Missing required fields
        resp = client.post('/api/i18n/',
                           json={'key': 'test_key'},  # Missing 'value'
                           headers=admin_headers)
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'Missing required fields' in data['message']


class TestTemplateEndpoints:
    """Test the templates API endpoints."""

    @pytest.fixture(autouse=True)
    def setup_templates(self, seeded_templates):
        """Autouse fixture to seed templates before tests."""
        pass
    """Test the templates API endpoints."""

    def test_get_templates_list(self, client):
        """Test getting the list of templates."""
        resp = client.get('/api/templates/')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'total' in data
        assert 'data' in data

        # items are directly in 'data' for paginated_response
        items = data['data']
        assert len(items) > 0

        # Verify template structure
        template = items[0]
        assert 'id' in template
        assert 'name' in template
        assert 'displayName' in template
        assert 'category' in template
        assert 'tags' in template

    def test_get_templates_by_category(self, client):
        """Test filtering templates by category."""
        resp = client.get('/api/templates/?category=landing')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

        # All templates should be in landing category
        items = data['data']['items']
        for template in items:
            assert template['category'] == 'landing'

    def test_get_templates_search(self, client):
        """Test searching templates by keyword."""
        resp = client.get('/api/templates/?search=landing')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

        # Should find landing templates
        items = data['data']['items']
        assert len(items) > 0

    def test_get_template_by_id(self, client):
        """Test getting a single template by ID."""
        # First, get a template ID
        list_resp = client.get('/api/templates/')
        template_id = list_resp.get_json()['data']['items'][0]['id']

        # Get the template
        resp = client.get(f'/api/templates/{template_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'template' in data['data']
        assert data['data']['template']['id'] == template_id

    def test_get_template_not_found(self, client):
        """Test getting a non-existent template."""
        resp = client.get('/api/templates/99999')
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['success'] is False
        assert 'not found' in data['message'].lower()

    def test_get_categories(self, client):
        """Test getting template categories."""
        resp = client.get('/api/templates/categories')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'categories' in data['data']

        categories = data['data']['categories']
        assert len(categories) > 0
        assert 'landing' in categories

    def test_get_tags(self, client):
        """Test getting template tags."""
        resp = client.get('/api/templates/tags')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'tags' in data['data']

        tags = data['data']['tags']
        assert isinstance(tags, list)

    def test_clone_template_requires_auth(self, client):
        """Test that cloning a template requires authentication."""
        resp = client.post('/api/templates/clone/1',
                           json={'name': 'Test Clone', 'subdomain': 'test-clone'})
        assert resp.status_code == 401  # Unauthorized

    def test_clone_template_success(self, client, user_token, flask_app):
        """Test successfully cloning a template."""
        # Get a template ID
        list_resp = client.get('/api/templates/')
        template_id = list_resp.get_json()['data']['items'][0]['id']

        # Clone the template
        resp = client.post(f'/api/templates/clone/{template_id}',
                           json={'name': 'Cloned Website', 'subdomain': 'cloned-site-test'},
                           headers={'Authorization': f'Bearer {user_token}'})

        assert resp.status_code == 201
        data = resp.get_json()
        assert data['success'] is True
        assert 'website' in data['data']

        website = data['data']['website']
        assert website['name'] == 'Cloned Website'
        assert website['subdomain'] == 'cloned-site-test'

    def test_clone_template_duplicate_subdomain(self, client, user_token, registered_website):
        """Test that cloning with a duplicate subdomain fails."""
        # Use the subdomain from the registered website
        subdomain = registered_website['subdomain']

        # Get a template ID
        list_resp = client.get('/api/templates/')
        template_id = list_resp.get_json()['data']['items'][0]['id']

        # Try to clone with duplicate subdomain
        resp = client.post(f'/api/templates/clone/{template_id}',
                           json={'name': 'Duplicate Name', 'subdomain': subdomain},
                           headers={'Authorization': f'Bearer {user_token}'})

        assert resp.status_code == 409  # Conflict
        data = resp.get_json()
        assert 'already taken' in data['message'].lower()

    def test_clone_template_missing_fields(self, client, user_token):
        """Test cloning a template with missing required fields."""
        # Get a template ID
        list_resp = client.get('/api/templates/')
        template_id = list_resp.get_json()['data']['items'][0]['id']

        # Try to clone without name
        resp = client.post(f'/api/templates/clone/{template_id}',
                           json={'subdomain': 'test-clone'},
                           headers={'Authorization': f'Bearer {user_token}'})

        assert resp.status_code == 400
        data = resp.get_json()
        assert 'Missing required fields' in data['message']

    def test_clone_template_not_found(self, client, user_token):
        """Test cloning a non-existent template."""
        resp = client.post('/api/templates/clone/999999',
                           json={'name': 'Test', 'subdomain': 'test-not-found'},
                           headers={'Authorization': f'Bearer {user_token}'})

        assert resp.status_code == 404
        data = resp.get_json()
        assert 'not found' in data['message'].lower()