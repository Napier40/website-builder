"""
Authentication Blueprint
Routes: /api/auth/register, /login, /me, /profile, /change-password
"""
import logging
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import create_access_token

from app.models.user import UserModel
from app.models.audit_log import AuditLogModel
from app.middleware.auth import jwt_required_custom
from app.utils.helpers import (
    validate_required_fields, validate_email,
    validate_password, error_response, success_response, get_client_ip
)

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    POST /api/auth/register
    Body: { name, email, password }
    """
    data = request.get_json()
    if not data:
        return error_response('Request body must be JSON', 400)

    # Validate required fields
    missing = validate_required_fields(data, ['name', 'email', 'password'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    # Validate email format
    if not validate_email(data['email']):
        return error_response('Please provide a valid email address', 400)

    # Validate password strength
    valid_pw, pw_error = validate_password(data['password'])
    if not valid_pw:
        return error_response(pw_error, 400)

    try:
        user = UserModel.create(
            name=data['name'],
            email=data['email'],
            password=data['password']
        )

        # Generate JWT token using user's _id as identity
        token = create_access_token(identity=str(user['_id']))

        # Audit log
        AuditLogModel.create_log(
            user_id=str(user['_id']),
            action='REGISTER',
            resource='/api/auth/register',
            details={'name': user['name'], 'email': user['email']},
            ip_address=get_client_ip()
        )

        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': user,
            'token': token
        }), 201

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Register error: {e}")
        return error_response('Server error during registration', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and return a JWT token.
    POST /api/auth/login
    Body: { email, password }
    """
    data = request.get_json()
    if not data:
        return error_response('Request body must be JSON', 400)

    missing = validate_required_fields(data, ['email', 'password'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    try:
        # Find user including password hash
        user = UserModel.find_by_email(data['email'], include_password=True)
        if not user:
            return error_response('Invalid email or password', 401)

        # Verify password
        if not UserModel.verify_password(data['password'], user.get('password', '')):
            return error_response('Invalid email or password', 401)

        # Check if account is active
        if not user.get('isActive', True):
            return error_response('Account is deactivated. Please contact support.', 403)

        # Sanitize before returning
        safe_user = UserModel.sanitize(user)
        token = create_access_token(identity=str(safe_user['_id']))

        # Audit log
        AuditLogModel.create_log(
            user_id=str(safe_user['_id']),
            action='LOGIN',
            resource='/api/auth/login',
            ip_address=get_client_ip(),
            user_agent=request.headers.get('User-Agent', '')
        )

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': safe_user,
            'token': token
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return error_response('Server error during login', 500)


@auth_bp.route('/me', methods=['GET'])
@jwt_required_custom
def get_me():
    """
    Get the currently authenticated user's profile.
    GET /api/auth/me
    Headers: Authorization: Bearer <token>
    """
    return jsonify({
        'success': True,
        'user': g.current_user
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required_custom
def update_profile():
    """
    Update the current user's name or email.
    PUT /api/auth/profile
    Body: { name?, email? }
    """
    data = request.get_json()
    if not data:
        return error_response('Request body must be JSON', 400)

    updates = {}
    if 'name' in data and data['name'].strip():
        updates['name'] = data['name'].strip()
    if 'email' in data:
        if not validate_email(data['email']):
            return error_response('Please provide a valid email address', 400)
        updates['email'] = data['email'].lower().strip()

    if not updates:
        return error_response('No valid fields to update', 400)

    try:
        updated_user = UserModel.update_by_id(g.user_id, updates)
        if not updated_user:
            return error_response('User not found', 404)

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': updated_user
        }), 200

    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return error_response('Server error updating profile', 500)


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required_custom
def change_password():
    """
    Change the current user's password.
    PUT /api/auth/change-password
    Body: { currentPassword, newPassword }
    """
    data = request.get_json()
    if not data:
        return error_response('Request body must be JSON', 400)

    missing = validate_required_fields(data, ['currentPassword', 'newPassword'])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}", 400)

    # Validate new password strength
    valid_pw, pw_error = validate_password(data['newPassword'])
    if not valid_pw:
        return error_response(pw_error, 400)

    try:
        # Get user with password
        user = UserModel.find_by_id(g.user_id, include_password=True)
        if not user:
            return error_response('User not found', 404)

        # Verify current password
        if not UserModel.verify_password(data['currentPassword'], user.get('password', '')):
            return error_response('Current password is incorrect', 401)

        # Update password
        success = UserModel.update_password(g.user_id, data['newPassword'])
        if not success:
            return error_response('Failed to update password', 500)

        # Audit log
        AuditLogModel.create_log(
            user_id=g.user_id,
            action='UPDATE',
            resource='/api/auth/change-password',
            details={'action': 'PASSWORD_CHANGE'},
            ip_address=get_client_ip()
        )

        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200

    except Exception as e:
        logger.error(f"Change password error: {e}")
        return error_response('Server error changing password', 500)