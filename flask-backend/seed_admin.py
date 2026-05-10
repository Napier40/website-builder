"""
Seed the default admin user.

Creates (or ensures) an admin account matching the credentials advertised
in the README and startup scripts:

    Email:    admin@websitebuilder.com
    Password: Admin@1234
    Role:     admin

Idempotent: if the user already exists with the right role, does nothing.
If a user with the email exists but is not an admin, promotes them.

Override with env vars if you want something else:
    ADMIN_EMAIL=you@example.com ADMIN_PASSWORD=Secret123 python seed_admin.py
"""
import os
import sys
from app import create_app
from app.database import db
from app.models.user import User


ADMIN_NAME     = os.environ.get('ADMIN_NAME',     'Administrator')
ADMIN_EMAIL    = os.environ.get('ADMIN_EMAIL',    'admin@websitebuilder.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@1234')


def seed_admin():
    app = create_app('development')
    with app.app_context():
        existing = User.query.filter_by(email=ADMIN_EMAIL.lower()).first()

        if existing:
            if existing.role != 'admin':
                existing.role = 'admin'
                db.session.commit()
                print(f'✓ Promoted existing user to admin: {ADMIN_EMAIL}')
            else:
                print(f'✓ Admin already exists: {ADMIN_EMAIL} (no changes made)')
            return existing

        user = User.create(
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            role='admin',
        )
        print('=' * 60)
        print('Admin user created successfully!')
        print('=' * 60)
        print(f'  Email:    {ADMIN_EMAIL}')
        print(f'  Password: {ADMIN_PASSWORD}')
        print(f'  Role:     admin')
        print('=' * 60)
        print('Change this password in production.')
        return user


if __name__ == '__main__':
    try:
        seed_admin()
    except Exception as exc:
        print(f'ERROR: Failed to seed admin user: {exc}', file=sys.stderr)
        sys.exit(1)
