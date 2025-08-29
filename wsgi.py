"""
WSGI entry point for production deployment
"""
from app import app
import os
import sys
from pathlib import Path

# Add project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('POCKETOJ_CONFIG', 'config.prod.yaml')


if __name__ == "__main__":
    app.run()
