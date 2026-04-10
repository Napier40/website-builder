"""
Auth Blueprint — register, login, profile
"""
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import create_access_token

from app.models.user      import User
from app.models.audit_log import AuditLog
from app.middleware.auth  import jwt_required_custom
from app.utils.helpers    import (success_response, error_response,
                                   validate_required_fields, validate_email,
                                   validate_password)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data:
        return error_response('Request body must be JSON', 400)

    missing = validate_required_fields(data, ['name', 'email', 'password'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    if not validate_email(data['email']):
        return error_response('Invalid email address', 400)

    valid_pw, pw_msg = validate_password(data['password'])
    if not valid_pw:
        return error_response(pw_msg, 400)

    try:
        user = User.create(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'user'),
        )
    except ValueError as e:
        return error_response(str(e), 409)
    except Exception as e:
        return error_response(f'Registration failed: {e}', 500)

    token = create_access_token(identity=str(user.id))
    AuditLog.create_log(user_id=user.id, action='REGISTER',
                        resource_model='User', resource_id=user.id)

    return success_response(
        data={'user': user.to_dict(), 'token': token},
        message='Registration successful',
        status_code=201,
    )


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return error_response('Request body must be JSON', 400)

    missing = validate_required_fields(data, ['email', 'password'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    user = User.find_by_email(data['email'])
    if not user or not user.verify_password(data['password']):
        return error_response('Invalid email or password', 401)

    token = create_access_token(identity=str(user.id))
    AuditLog.create_log(user_id=user.id, action='LOGIN',
                        resource_model='User', resource_id=user.id)

    return success_response(
        data={'user': user.to_dict(), 'token': token},
        message='Login successful',
    )


@auth_bp.route('/me', methods=['GET'])
@jwt_required_custom
def get_me():
    return success_response(data={'user': g.current_user.to_dict()})


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required_custom
def update_profile():
    data = request.get_json(silent=True)
    if not data:
        return error_response('Request body must be JSON', 400)

    allowed = {}
    if 'name' in data and data['name'].strip():
        allowed['name'] = data['name'].strip()

    if not allowed:
        return error_response('No valid fields to update', 400)

    g.current_user.update(**allowed)
    return success_response(
        data={'user': g.current_user.to_dict()},
        message='Profile updated',
    )


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required_custom
def change_password():
    data = request.get_json(silent=True)
    if not data:
        return error_response('Request body must be JSON', 400)

    missing = validate_required_fields(data, ['currentPassword', 'newPassword'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    if not g.current_user.verify_password(data['currentPassword']):
        return error_response('Current password is incorrect', 401)

    valid_pw, pw_msg = validate_password(data['newPassword'])
    if not valid_pw:
        return error_response(pw_msg, 400)

    g.current_user.update_password(data['newPassword'])
    AuditLog.create_log(user_id=g.current_user.id, action='UPDATE',
                        resource_model='User', resource_id=g.current_user.id,
                        description='Password changed')

    return success_response(message='Password changed successfully')