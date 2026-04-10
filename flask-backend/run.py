"""
Flask Application Entry Point

Usage:
    python run.py                                      # development server
    flask run                                          # flask CLI
    gunicorn -w 4 -b 0.0.0.0:5000 "run:app"          # production

No database installation required — SQLite is built into Python.
The database file (website_builder.db) is created automatically on first run.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port  = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'

    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    db_path = db_uri.replace('sqlite:///', '') if 'memory' not in db_uri else ':memory:'

    print(f"\n{'='*54}")
    print(f"  Website Builder API  —  Python Flask + SQLite")
    print(f"{'='*54}")
    print(f"  URL:         http://localhost:{port}")
    print(f"  Health:      http://localhost:{port}/api/health")
    print(f"  Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"  Debug mode:  {debug}")
    print(f"  Database:    SQLite  →  {db_path}")
    print(f"{'='*54}\n")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
    )