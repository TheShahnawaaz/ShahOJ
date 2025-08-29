#!/bin/bash
# Simple Azure startup script for ShahOJ - Minimal approach

echo "🚀 Simple startup for ShahOJ"

# Set basic environment variables
export FLASK_ENV=production
export POCKETOJ_CONFIG=config.prod.yaml

# Use python3 directly
PYTHON_CMD="python3"

# Try to run with gunicorn, fallback to Flask
if $PYTHON_CMD -c "import gunicorn" 2>/dev/null; then
    echo "✅ Starting with Gunicorn"
    exec $PYTHON_CMD -m gunicorn wsgi:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --access-logfile -
else
    echo "⚠️  Starting with Flask (development mode)"
    exec $PYTHON_CMD wsgi.py
fi
