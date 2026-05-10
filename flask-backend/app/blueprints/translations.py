"""
Translations Blueprint — Multilingual support with English as principal language
"""
from flask import Blueprint, request, g
from sqlalchemy.exc import IntegrityError

from app.models.translation import Translation
from app.middleware.auth      import jwt_required_custom, authorize
from app.utils.helpers        import (success_response, error_response,
                                       paginated_response, get_pagination_params,
                                       validate_required_fields)

translations_bp = Blueprint('i18n', __name__)


@translations_bp.route('/', methods=['GET'])
def get_translations():
    """
    Get translations by language and namespace.
    Query params:
        - language (default: 'en')
        - namespace (optional)
    Returns a flat dict if namespace specified, otherwise grouped by namespace.
    """
    language = request.args.get('language', 'en').lower()
    namespace = request.args.get('namespace')

    translations = Translation.get_all_by_language(language, namespace)

    if namespace:
        # Flat dictionary for single namespace
        return success_response(data={
            'language': language,
            'namespace': namespace,
            'translations': translations,
        })
    else:
        # Grouped by namespace
        return success_response(data={
            'language': language,
            'translations': translations,
        })


@translations_bp.route('/keys/<key>', methods=['GET'])
def get_translation(key):
    """
    Get a single translation by key.
    Falls back to English if the requested language doesn't exist.
    """
    language = request.args.get('language', 'en').lower()
    namespace = request.args.get('namespace')

    translation = Translation.find_by_key(key, language, namespace)

    if not translation:
        return error_response(f'Translation not found for key: {key}', 404)

    return success_response(data={
        'key':        translation.key,
        'language':   translation.language,
        'value':      translation.value,
        'namespace':  translation.namespace,
    })


@translations_bp.route('/languages', methods=['GET'])
def get_languages():
    """Return list of supported languages."""
    languages = Translation.get_supported_languages()
    return success_response(data={'languages': languages})


@translations_bp.route('/', methods=['POST'])
@jwt_required_custom
@authorize('admin')
def create_translation():
    """Create a new translation (admin only)."""
    data = request.get_json(silent=True) or {}
    missing = validate_required_fields(data, ['key', 'language', 'value'])
    if missing:
        return error_response(f'Missing required fields: {", ".join(missing)}', 400)

    try:
        translation = Translation.upsert(
            key=data['key'],
            language=data['language'],
            value=data['value'],
            namespace=data.get('namespace'),
            context=data.get('context'),
        )
        return success_response(
            data={'translation': translation.to_dict()},
            message='Translation created',
            status_code=201,
        )
    except IntegrityError:
        from app.database import db
        db.session.rollback()
        return error_response('Translation with this key/language/namespace already exists', 409)
    except Exception as e:
        from app.database import db
        db.session.rollback()
        return error_response(f'Failed to create translation: {e}', 500)


@translations_bp.route('/bulk', methods=['POST'])
@jwt_required_custom
@authorize('admin')
def bulk_upsert_translations():
    """
    Bulk insert/update translations.
    Body can be:
        - Flat: {key: value, ...}
        - Grouped: {namespace: {key: value, ...}, ...}
    Query param: language (default: 'en')
    """
    data = request.get_json(silent=True) or {}
    if not data:
        return error_response('Request body must contain translations', 400)

    language = request.form.get('language') or request.args.get('language', 'en')

    try:
        count = Translation.bulk_upsert(data, language)
        return success_response(
            data={'count': count, 'language': language},
            message=f'Successfully upserted {count} translations',
        )
    except Exception as e:
        from app.database import db
        db.session.rollback()
        return error_response(f'Failed to bulk upsert translations: {e}', 500)


@translations_bp.route('/<int:translation_id>', methods=['PUT'])
@jwt_required_custom
@authorize('admin')
def update_translation(translation_id):
    """Update a translation (admin only)."""
    translation = Translation.query.get(translation_id)
    if not translation:
        return error_response('Translation not found', 404)

    data = request.get_json(silent=True) or {}
    allowed = {k: v for k, v in data.items()
               if k in ('key', 'value', 'namespace', 'context')}

    if not allowed:
        return error_response('No valid fields to update', 400)

    try:
        for key, value in allowed.items():
            setattr(translation, key, value)
        from app.database import db
        db.session.commit()
        return success_response(
            data={'translation': translation.to_dict()},
            message='Translation updated',
        )
    except IntegrityError:
        from app.database import db
        db.session.rollback()
        return error_response('Translation with this key/language/namespace already exists', 409)
    except Exception as e:
        from app.database import db
        db.session.rollback()
        return error_response(f'Failed to update translation: {e}', 500)


@translations_bp.route('/<int:translation_id>', methods=['DELETE'])
@jwt_required_custom
@authorize('admin')
def delete_translation(translation_id):
    """Delete a translation (admin only)."""
    translation = Translation.query.get(translation_id)
    if not translation:
        return error_response('Translation not found', 404)

    from app.database import db
    db.session.delete(translation)
    db.session.commit()

    return success_response(message='Translation deleted')