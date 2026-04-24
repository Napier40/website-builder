"""
Auth Blueprint — register, login, profile
"""
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta, timezone
import secrets
import hashlib

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

    # Allow email update if provided and different
    if 'email' in data and data['email'].strip():
        new_email = data['email'].strip().lower()
        if not validate_email(new_email):
            return error_response('Invalid email address', 400)
        if new_email != g.current_user.email:
            existing = User.find_by_email(new_email)
            if existing:
                return error_response('Email already in use', 409)
            # Update email directly via SQLAlchemy
            from app.database import db
            from datetime import datetime, timezone
            g.current_user.email = new_email
            g.current_user.updated_at = datetime.now(timezone.utc)
            db.session.commit()

    if allowed:
        g.current_user.update(**allowed)

    return success_response(
        data={'user': g.current_user.to_dict()},
        message='Profile updated',
    )


@auth_bp.route('/me', methods=['DELETE'])
@jwt_required_custom
def delete_account():
    """Delete the current user's account and all associated data."""
    user = g.current_user
    user_id = user.id
    user.delete()
    AuditLog.create_log(user_id=user_id, action='DELETE',
                        resource_model='User', resource_id=user_id,
                        description='Account deleted by user')
    return success_response(message='Account deleted successfully')


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

# In-memory token store for password resets (in production, use Redis or database)
_password_reset_tokens = {}


def _generate_reset_token():
    """Generate a secure reset token."""
    return secrets.token_urlsafe(32)


def _hash_token(token):
    """Hash a token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Initiate password reset process."""
    data = request.get_json(silent=True)
    if not data:
        return error_response('Request body must be JSON', 400)
    
    email = data.get('email', '').strip().lower()
    if not email:
        return error_response('Email is required', 400)
    
    if not validate_email(email):
        return error_response('Invalid email address', 400)
    
    user = User.find_by_email(email)
    if not user:
        # Don't reveal whether user exists
        return success_response(
            message='If an account with that email exists, a reset link has been sent.'
        )
    
    # Generate and store token
    token = _generate_reset_token()
    token_hash = _hash_token(token)
    expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    
    _password_reset_tokens[token_hash] = {
        'user_id': user.id,
        'expiry': expiry,
        'used': False
    }
    
    # In production, send email with reset link
    # For now, return the token for testing
    AuditLog.create_log(
        user_id=user.id, 
        action='PASSWORD_RESET_REQUEST',
        resource_model='User', 
        resource_id=user.id,
        description='Password reset requested'
    )
    
    return success_response(
        message='If an account with that email exists, a reset link has been sent.',
        data={'reset_token': token}  # Remove in production
    )


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token."""
    data = request.get_json(silent=True)
    if not data:
        return error_response('Request body must be JSON', 400)
    
    token = data.get('token', '').strip()
    new_password = data.get('password', '').strip()
    
    if not token or not new_password:
        return error_response('Token and new password are required', 400)
    
    valid_pw, pw_msg = validate_password(new_password)
    if not valid_pw:
        return error_response(pw_msg, 400)
    
    token_hash = _hash_token(token)
    token_data = _password_reset_tokens.get(token_hash)
    
    if not token_data:
        return error_response('Invalid or expired reset token', 400)
    
    if token_data['used']:
        return error_response('Reset token has already been used', 400)
    
    if datetime.now(timezone.utc) > token_data['expiry']:
        del _password_reset_tokens[token_hash]
        return error_response('Reset token has expired', 400)
    
    user = User.find_by_id(token_data['user_id'])
    if not user:
        return error_response('User not found', 404)
    
    # Update password and mark token as used
    user.update_password(new_password)
    token_data['used'] = True
    
    AuditLog.create_log(
        user_id=user.id, 
        action='PASSWORD_RESET_COMPLETE',
        resource_model='User', 
        resource_id=user.id,
        description='Password reset completed'
    )
    
    return success_response(message='Password has been reset successfully')


@auth_bp.route('/validate-reset-token', methods=['POST'])
def validate_reset_token():
    """Validate if a reset token is still valid."""
    data = request.get_json(silent=True)
    if not data:
        return error_response('Request body must be JSON', 400)
    
    token = data.get('token', '').strip()
    if not token:
        return error_response('Token is required', 400)
    
    token_hash = _hash_token(token)
    token_data = _password_reset_tokens.get(token_hash)
    
    if not token_data:
        return success_response(
            data={'valid': False},
            message='Invalid reset token'
        )
    
    if token_data['used']:
        return success_response(
            data={'valid': False},
            message='Reset token has already been used'
        )
    
    if datetime.now(timezone.utc) > token_data['expiry']:
        del _password_reset_tokens[token_hash]
        return success_response(
            data={'valid': False},
            message='Reset token has expired'
        )
    
    return success_response(
        data={'valid': True},
        message='Token is valid'
    )
