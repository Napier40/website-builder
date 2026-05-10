"""
Site Rendering Blueprints
─────────────────────────
Two blueprints that turn a Website's JSON trees into live HTML:

  • preview_bp    → GET /api/websites/<id>/preview[/<slug>]
                    Authenticated editor preview — owner/admin only,
                    renders the draft tree (or legacy raw HTML fallback)
                    inside a complete Bootstrap 5.3 document.

  • public_bp     → GET /s/<subdomain>[/<slug>]
                    Public-facing published site. No auth required.
                    Only serves sites with is_published=True.

Both share the same underlying renderer so the editor iframe sees
exactly what the world will see after publish.
"""
from __future__ import annotations

from flask import Blueprint, Response, request, g

from app.models.website           import Website, Page
from app.middleware.auth          import jwt_required_custom
from app.services.bootstrap_renderer import render_page
from app.services.bootstrap_themes   import theme_exists
from app.utils.helpers             import error_response

# ─── Editor preview (authenticated) ───────────────────────────────────────────
preview_bp = Blueprint('preview', __name__)


def _render_page_html(website: Website, page: Page, *, draft: bool) -> str:
    """
    Produce a complete HTML document for a single page.

    If the page has a JSON tree, render it through bootstrap_renderer.
    Otherwise fall back to the legacy raw-HTML `content` field wrapped in
    a minimal themed document so pre-builder sites still display.
    """
    theme = website.theme or 'default'
    if not theme_exists(theme):
        theme = 'default'

    title = f"{page.title} — {website.name}"
    description = website.description or ''

    tree = page.tree
    if tree:
        return render_page(
            tree,
            title=title,
            theme=theme,
            description=description,
        )

    # Legacy raw-HTML fallback — still theme it for consistency.
    legacy_tree = {
        'type': 'container',
        'props': {'fluid': False, 'paddingY': 'py-4'},
        'children': [{
            'type':  'html',
            'props': {'html': page.content or '<p class="text-muted">This page is empty.</p>'},
        }],
    }
    return render_page(
        legacy_tree,
        title=title + (' (draft)' if draft else ''),
        theme=theme,
        description=description,
    )


def _pick_page(website: Website, slug: str | None) -> Page | None:
    """Return the matching page by slug, or the first page if slug is None."""
    if not website.pages:
        return None
    if slug:
        for p in website.pages:
            if p.slug == slug:
                return p
        return None
    return website.pages[0]


@preview_bp.route('/<int:website_id>/preview', methods=['GET'], strict_slashes=False)
@preview_bp.route('/<int:website_id>/preview/<slug>', methods=['GET'])
@jwt_required_custom
def preview_website(website_id, slug=None):
    """Editor-only full-page preview. Owner or admin only."""
    website = Website.find_by_id(website_id)
    if not website:
        return error_response('Website not found', 404)
    if website.user_id != g.current_user.id and g.current_user.role != 'admin':
        return error_response('Access denied', 403)

    page = _pick_page(website, slug)
    if not page:
        html = render_page(
            {
                'type': 'alert',
                'props': {
                    'variant': 'alert-warning',
                    'message': 'This website has no pages yet. Add a page to preview it.',
                },
            },
            title=f"{website.name} — empty",
            theme=website.theme or 'default',
        )
        return Response(html, mimetype='text/html', status=200)

    html = _render_page_html(website, page, draft=True)
    resp = Response(html, mimetype='text/html', status=200)
    # Editor preview must never be cached — it needs to reflect fresh edits.
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp


# ─── Public published-site serving (unauthenticated) ──────────────────────────
public_bp = Blueprint('public', __name__)


@public_bp.route('/s/<subdomain>', methods=['GET'], strict_slashes=False)
@public_bp.route('/s/<subdomain>/<slug>', methods=['GET'])
def serve_published_site(subdomain, slug=None):
    """Public page view. No auth. Only serves published + approved sites."""
    website = Website.query.filter_by(subdomain=subdomain.lower()).first()
    if not website:
        return _not_found_response(subdomain)

    # Only published sites are publicly visible.
    if not website.is_published or website.moderation_status != 'approved':
        return _not_found_response(subdomain)

    page = _pick_page(website, slug)
    if not page:
        return _not_found_response(subdomain, website=website)

    html = _render_page_html(website, page, draft=False)
    resp = Response(html, mimetype='text/html', status=200)
    # Short cache — enough to absorb bursts, short enough that republishes
    # propagate quickly.
    resp.headers['Cache-Control'] = 'public, max-age=60'
    return resp


def _not_found_response(subdomain: str, website: Website | None = None) -> Response:
    """Render a themed 404 using the site's chosen theme when possible."""
    theme = website.theme if (website and theme_exists(website.theme or '')) else 'default'
    html = render_page(
        {
            'type': 'section',
            'props': {'paddingY': 'py-5', 'bg': ''},
            'children': [
                {
                    'type': 'container',
                    'props': {'fluid': False},
                    'children': [
                        {'type': 'heading', 'props': {'level': 'h1', 'text': '404 — Page not found'}},
                        {'type': 'paragraph', 'props': {
                            'text': f'The site “{subdomain}” is not available, '
                                    'or the page you requested does not exist.',
                            'leadClass': 'lead',
                        }},
                    ],
                },
            ],
        },
        title=f"404 — {subdomain}",
        theme=theme,
    )
    resp = Response(html, mimetype='text/html', status=404)
    resp.headers['Cache-Control'] = 'no-store'
    return resp
