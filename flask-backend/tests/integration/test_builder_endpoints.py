"""
Integration tests for the new builder endpoints:
  • GET /api/catalogue
  • GET /api/catalogue/components
  • GET /api/catalogue/themes
  • GET /api/websites/<id>/preview     (authenticated)
  • GET /s/<subdomain>                 (public)
  • PUT /api/websites/<id>             (theme update)
"""
import pytest


# ─── /api/catalogue ──────────────────────────────────────────────────────────

class TestCatalogueEndpoints:
    def test_full_catalogue(self, client):
        resp = client.get('/api/catalogue')
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['success'] is True

        data = body['data']
        # Version info
        assert data['bootstrapVersion'].startswith('5.3.')
        assert data['bootswatchVersion'].startswith('5.3.')
        # CDN URLs
        assert data['cdn']['bootstrapCss'].startswith('https://cdn.jsdelivr.net/')
        assert data['cdn']['bootstrapJs'].startswith('https://cdn.jsdelivr.net/')
        assert data['cdn']['iconsCss'].startswith('https://cdn.jsdelivr.net/')
        # Components & themes
        assert isinstance(data['components'], list)
        assert len(data['components']) >= 69   # all Bootstrap 5.3 elements
        assert isinstance(data['themes'], list)
        assert len(data['themes']) == 27       # default + 26 Bootswatch

    def test_components_only(self, client):
        resp = client.get('/api/catalogue/components')
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert len(data['components']) >= 69
        # Every component must have the fields the frontend needs.
        for comp in data['components']:
            assert 'type'     in comp
            assert 'category' in comp
            assert 'label'    in comp
            assert 'props'    in comp

    def test_themes_only(self, client):
        resp = client.get('/api/catalogue/themes')
        assert resp.status_code == 200
        data = resp.get_json()['data']
        assert len(data['themes']) == 27
        slugs = [t['slug'] for t in data['themes']]
        assert 'default' in slugs
        assert 'cosmo'   in slugs
        assert 'darkly'  in slugs
        assert 'vapor'   in slugs
        # Every theme should expose a CDN CSS URL
        for t in data['themes']:
            assert t['cssUrl'].startswith('https://')

    def test_catalogue_is_public(self, client):
        """No auth required — the palette must load before sign-in."""
        assert client.get('/api/catalogue').status_code          == 200
        assert client.get('/api/catalogue/themes').status_code   == 200
        assert client.get('/api/catalogue/components').status_code == 200


# ─── Editor preview ──────────────────────────────────────────────────────────

def _make_website(flask_app, user_id, *, theme='cosmo', subdomain='preview-site',
                  tree=None, published=False):
    from app.database import db
    from app.models.website import Website
    with flask_app.app_context():
        w = Website.create(name='Preview Site', subdomain=subdomain,
                           user_id=user_id, theme=theme)
        if tree is not None:
            w.pages[0].tree = tree
            db.session.commit()
        if published:
            w.publish()
        return w.id


class TestPreviewEndpoint:
    def _tree(self):
        return {
            'type': 'container', 'props': {'fluid': False, 'paddingY': 'py-5'},
            'children': [
                {'type': 'heading',   'props': {'level': 'h1', 'text': 'Hello Preview'}},
                {'type': 'paragraph', 'props': {'text': 'Body text for preview.'}},
            ],
        }

    def test_requires_auth(self, client, registered_user, flask_app):
        wid = _make_website(flask_app, registered_user['id'], tree=self._tree())
        resp = client.get(f'/api/websites/{wid}/preview')
        assert resp.status_code == 401

    def test_owner_can_preview(self, client, registered_user, user_token, flask_app):
        wid = _make_website(flask_app, registered_user['id'], tree=self._tree(),
                            theme='darkly')
        resp = client.get(f'/api/websites/{wid}/preview',
                          headers={'Authorization': f'Bearer {user_token}'})
        assert resp.status_code == 200
        assert resp.mimetype == 'text/html'
        html = resp.get_data(as_text=True)
        assert 'Hello Preview' in html
        assert 'darkly' in html            # bootswatch URL contains the slug
        assert 'bootstrap.min.css' in html
        # Preview must never be cached
        assert 'no-store' in resp.headers.get('Cache-Control', '')

    def test_other_user_forbidden(self, client, flask_app, user_token):
        """A second user cannot preview the first user's site."""
        from app.models.user import User
        with flask_app.app_context():
            owner = User.create(name='Owner', email='owner@example.com',
                                password='password123')
            wid = _make_website(flask_app, owner.id, tree=self._tree(),
                                subdomain='owner-site')
        resp = client.get(f'/api/websites/{wid}/preview',
                          headers={'Authorization': f'Bearer {user_token}'})
        assert resp.status_code == 403

    def test_preview_without_tree_uses_legacy_content(self, client, registered_user,
                                                     user_token, flask_app):
        """Legacy pages (no JSON tree) still render via raw-HTML fallback."""
        from app.database import db
        from app.models.website import Website
        with flask_app.app_context():
            w = Website.create(name='Legacy', subdomain='legacy-site',
                               user_id=registered_user['id'])
            w.pages[0].content = '<h1>Legacy Heading</h1><p>raw html</p>'
            db.session.commit()
            wid = w.id

        resp = client.get(f'/api/websites/{wid}/preview',
                          headers={'Authorization': f'Bearer {user_token}'})
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert 'Legacy Heading' in html


# ─── Public site serving ─────────────────────────────────────────────────────

class TestPublicSite:
    def _tree(self):
        return {
            'type': 'container', 'props': {'fluid': False},
            'children': [
                {'type': 'heading', 'props': {'level': 'h1', 'text': 'Public Home'}},
            ],
        }

    def test_published_site_is_public(self, client, registered_user, flask_app):
        _make_website(flask_app, registered_user['id'], tree=self._tree(),
                      subdomain='my-public-site', published=True, theme='cosmo')
        resp = client.get('/s/my-public-site')
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert 'Public Home' in html
        assert 'cosmo' in html
        assert resp.headers.get('Cache-Control', '').startswith('public, max-age=')

    def test_slug_routing(self, client, registered_user, flask_app):
        _make_website(flask_app, registered_user['id'], tree=self._tree(),
                      subdomain='slug-site', published=True)
        # First page ('home') is accessible by slug.
        r = client.get('/s/slug-site/home')
        assert r.status_code == 200
        # Unknown slug → 404.
        r = client.get('/s/slug-site/does-not-exist')
        assert r.status_code == 404

    def test_unpublished_site_is_404(self, client, registered_user, flask_app):
        _make_website(flask_app, registered_user['id'], tree=self._tree(),
                      subdomain='draft-site', published=False)
        resp = client.get('/s/draft-site')
        assert resp.status_code == 404

    def test_unknown_subdomain_is_404(self, client):
        resp = client.get('/s/does-not-exist-at-all')
        assert resp.status_code == 404

    def test_404_is_themed(self, client, registered_user, flask_app):
        _make_website(flask_app, registered_user['id'], tree=self._tree(),
                      subdomain='darkly-site', published=True, theme='darkly')
        r = client.get('/s/darkly-site/no-such-page')
        assert r.status_code == 404
        html = r.get_data(as_text=True)
        # Even 404 pages should wear the site's chosen theme
        assert 'darkly' in html


# ─── Theme-update PUT ────────────────────────────────────────────────────────

class TestThemeUpdate:
    def test_update_theme(self, client, registered_user, user_token, flask_app):
        wid = _make_website(flask_app, registered_user['id'])
        resp = client.put(f'/api/websites/{wid}',
                          json={'theme': 'vapor'},
                          headers={'Authorization': f'Bearer {user_token}'})
        assert resp.status_code == 200
        assert resp.get_json()['data']['website']['theme'] == 'vapor'

    def test_reject_unknown_theme(self, client, registered_user, user_token, flask_app):
        wid = _make_website(flask_app, registered_user['id'])
        resp = client.put(f'/api/websites/{wid}',
                          json={'theme': 'not-a-theme'},
                          headers={'Authorization': f'Bearer {user_token}'})
        assert resp.status_code == 400
        assert 'Unknown theme' in resp.get_json()['message']

    def test_create_with_theme(self, client, user_token):
        resp = client.post('/api/websites/',
                           json={'name':'T', 'subdomain':'themed-create', 'theme':'lux'},
                           headers={'Authorization': f'Bearer {user_token}'})
        assert resp.status_code == 201
        assert resp.get_json()['data']['website']['theme'] == 'lux'
