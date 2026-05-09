"""
Catalogue Blueprint
───────────────────
Exposes the static design-time data the React builder needs:

  • GET /api/catalogue            → component catalogue + themes + CDN URLs
  • GET /api/catalogue/components → just the component schema
  • GET /api/catalogue/themes     → just the theme list

These endpoints are **public** — no auth required — because the data is
purely descriptive and needed before the user is logged in (e.g. on the
marketing-site preview page).
"""
from flask import Blueprint, jsonify

from app.services.component_catalogue import get_catalogue
from app.services.bootstrap_themes    import (
    THEMES, BOOTSTRAP_VERSION, BOOTSWATCH_VERSION,
    BOOTSTRAP_CSS, BOOTSTRAP_JS, BOOTSTRAP_ICONS_CSS,
    theme_css_url,
)

catalogue_bp = Blueprint('catalogue', __name__)


def _themes_payload():
    """Serialise the theme table with CDN URLs ready for the frontend."""
    return [
        {
            'slug':        t['slug'],
            'name':        t['name'],
            'description': t.get('description', ''),
            'isDark':      t.get('is_dark', False),
            'cssUrl':      theme_css_url(t['slug']),
        }
        for t in THEMES
    ]


@catalogue_bp.route('', methods=['GET'])
@catalogue_bp.route('/', methods=['GET'])
def get_full_catalogue():
    """Full payload — everything the builder needs at startup."""
    return jsonify({
        'success': True,
        'data': {
            'bootstrapVersion': BOOTSTRAP_VERSION,
            'bootswatchVersion': BOOTSWATCH_VERSION,
            'cdn': {
                'bootstrapCss': BOOTSTRAP_CSS,
                'bootstrapJs':  BOOTSTRAP_JS,
                'iconsCss':     BOOTSTRAP_ICONS_CSS,
            },
            'components': get_catalogue(),
            'themes':     _themes_payload(),
        },
    }), 200


@catalogue_bp.route('/components', methods=['GET'])
def get_components():
    return jsonify({
        'success': True,
        'data': {'components': get_catalogue()},
    }), 200


@catalogue_bp.route('/themes', methods=['GET'])
def get_themes():
    return jsonify({
        'success': True,
        'data': {
            'bootstrapVersion':  BOOTSTRAP_VERSION,
            'bootswatchVersion': BOOTSWATCH_VERSION,
            'themes':            _themes_payload(),
        },
    }), 200
