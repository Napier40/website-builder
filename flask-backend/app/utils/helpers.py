"""
Utility Helpers
Common helper functions used across blueprints
"""
import math
import re
from datetime import datetime, timezone
from functools import wraps
from flask import jsonify, request
import bleach


# ─── Database guard decorator ─────────────────────────────────────────────────

def db_required(f):
    """
    Placeholder — kept for compatibility.
    With SQLite this is never needed (DB is always available),
    but the decorator is preserved so imports don't break.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated


# ─── Response helpers ─────────────────────────────────────────────────────────

def success_response(data=None, message=None, status_code=200, **kwargs):
    """Build a standardised success JSON response."""
    body = {'success': True}
    if message:
        body['message'] = message
    if data is not None:
        body['data'] = data
    body.update(kwargs)
    return jsonify(body), status_code


def error_response(message: str, status_code: int = 400, errors: dict = None):
    """Build a standardised error JSON response."""
    body = {'success': False, 'message': message}
    if errors:
        body['errors'] = errors
    return jsonify(body), status_code


def paginated_response(items: list, total: int, page: int,
                       limit: int, **extra_fields):
    """Build a paginated response with metadata."""
    body = {
        'success': True,
        'count':   len(items),
        'total':   total,
        'page':    page,
        'pages':   math.ceil(total / limit) if limit > 0 else 1,
        'data':    items,
    }
    body.update(extra_fields)
    return jsonify(body), 200


# ─── Pagination helpers ───────────────────────────────────────────────────────

def get_pagination_params(default_limit: int = 10, max_limit: int = 100):
    """
    Extract and validate pagination parameters from request query string.
    Returns (page, limit, skip).
    """
    try:
        page = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1

    try:
        limit = min(max_limit, max(1, int(request.args.get('limit', default_limit))))
    except (ValueError, TypeError):
        limit = default_limit

    skip = (page - 1) * limit
    return page, limit, skip


def get_sort_params(default_field: str = 'created_at', default_dir: str = 'desc'):
    """
    Extract sort parameters from request query string.
    Prefix field with '-' for descending, e.g. ?sort=-created_at
    Returns (sort_field, sort_direction).
    """
    sort = request.args.get('sort', default_field)
    if sort.startswith('-'):
        return sort[1:], 'desc'
    return sort, 'asc' if sort != default_field else default_dir


# ─── Validation helpers ───────────────────────────────────────────────────────

def validate_required_fields(data: dict, required_fields: list) -> list:
    """
    Check that all required fields are present and non-empty.
    Returns a list of missing field names.
    """
    missing = []
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    return missing


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_subdomain(subdomain: str) -> bool:
    """
    Validate subdomain format:
    - 3-63 characters
    - lowercase letters, digits, hyphens only
    - cannot start or end with hyphen
    """
    if len(subdomain) < 3 or len(subdomain) > 63:
        return False
    pattern = r'^[a-z0-9][a-z0-9\-]*[a-z0-9]$'
    return bool(re.match(pattern, subdomain.lower()))


def validate_password(password: str) -> tuple:
    """
    Validate password strength.
    Returns (is_valid, error_message).
    """
    if len(password) < 6:
        return False, 'Password must be at least 6 characters long'
    if len(password) > 128:
        return False, 'Password must be less than 128 characters'
    return True, ''


# ─── Misc helpers ─────────────────────────────────────────────────────────────

def get_client_ip() -> str:
    """Extract real client IP from request, considering proxies."""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    return request.remote_addr or 'unknown'


# ─────────────────────────────────────────────────────────────────────────────
# Input Sanitization helpers
# ─────────────────────────────────────────────────────────────────────────────

# Allowed HTML tags for rich text content
ALLOWED_TAGS = [
    'a', 'abbr', 'article', 'b', 'blockquote', 'br', 'caption', 'code',
    'col', 'colgroup', 'dd', 'div', 'dl', 'dt', 'em', 'figcaption',
    'figure', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
    'li', 'ol', 'p', 'pre', 'q', 's', 'section', 'small', 'span',
    'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
    'thead', 'tr', 'u', 'ul'
]

# Allowed HTML attributes
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'style'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'table': ['border', 'cellpadding', 'cellspacing'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
}


def sanitize_html(content: str) -> str:
    """
    Sanitize HTML content by allowing only safe tags and attributes.
    Prevents XSS attacks while preserving formatting.
    """
    if not content:
        return ''
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


def strip_tags(content: str) -> str:
    """
    Remove all HTML tags from content.
    Use for plain text fields that should not contain any HTML.
    """
    if not content:
        return ''
    return bleach.clean(content, tags=[], attributes={}, strip=True)


def sanitize_input(value: str, max_length: int = None) -> str:
    """
    Sanitize a string input:
    - Strip HTML tags
    - Trim whitespace
    - Optionally truncate to max_length
    
    Use for names, titles, and other plain text fields.
    """
    if not value:
        return ''
    
    # Remove any HTML tags
    cleaned = strip_tags(str(value))
    
    # Trim whitespace
    cleaned = cleaned.strip()
    
    # Truncate if max_length specified
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned


def sanitize_url(url: str) -> str:
    """
    Sanitize a URL to ensure it uses a safe protocol.
    Only allows http, https, mailto, and tel protocols.
    """
    if not url:
        return ''
    
    url = url.strip()
    
    # List of allowed protocols
    allowed_protocols = ['http://', 'https://', 'mailto:', 'tel:', '/']
    
    # Check if URL starts with an allowed protocol
    for protocol in allowed_protocols:
        if url.lower().startswith(protocol):
            return url
    
    # If no protocol, assume https
    if not url.startswith('//'):
        return 'https://' + url
    
    # Block javascript: and other dangerous protocols
    return ''
