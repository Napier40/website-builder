"""
Flask Application Entry Point
Run this file to start the development server.
Usage:
    python run.py
    OR
    flask run
    OR (production)
    gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
"""
import os
from dotenv import load_dotenv

# Load environment variables before creating the app
load_dotenv()

from app import create_app

# Create the Flask application
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'

    print(f"\n{'='*50}")
    print(f"  Website Builder API - Python Flask")
    print(f"  Running on: http://localhost:{port}")
    print(f"  Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"  Debug mode: {debug}")
    print(f"{'='*50}\n")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )