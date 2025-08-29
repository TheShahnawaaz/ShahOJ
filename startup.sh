#!/bin/bash
# Azure App Service startup script for ShahOJ

echo "🚀 Starting ShahOJ on Azure App Service"
echo "========================================"

# Set environment variables for production
export FLASK_ENV=production
export POCKETOJ_CONFIG=config.prod.yaml

# Create necessary directories
mkdir -p /tmp/pocketoj
mkdir -p logs

# Find the Python virtual environment created by Azure
if [ -d "/opt/python/3.11/bin" ]; then
    export PATH="/opt/python/3.11/bin:$PATH"
elif [ -d "/opt/python/3.10/bin" ]; then
    export PATH="/opt/python/3.10/bin:$PATH"
elif [ -d "/opt/python/3.9/bin" ]; then
    export PATH="/opt/python/3.9/bin:$PATH"
fi

# Try to find the virtual environment
if [ -d "/home/site/wwwroot/antenv/bin" ]; then
    source /home/site/wwwroot/antenv/bin/activate
    echo "✅ Activated Azure virtual environment"
elif [ -d "/opt/python/current/bin" ]; then
    export PATH="/opt/python/current/bin:$PATH"
    echo "✅ Using Python current environment"
fi

# Generate secret key if not provided
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  WARNING: No SECRET_KEY environment variable set. Generating one..."
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "dev-secret-key")
    echo "✅ Generated SECRET_KEY"
fi

echo "🐍 Python version: $(python --version 2>/dev/null || python3 --version)"
echo "📦 Checking dependencies..."

# Verify gunicorn is available
if command -v gunicorn >/dev/null 2>&1; then
    echo "✅ Gunicorn found"
    GUNICORN_CMD="gunicorn"
elif python -c "import gunicorn" 2>/dev/null; then
    echo "✅ Gunicorn module found"
    GUNICORN_CMD="python -m gunicorn"
elif python3 -c "import gunicorn" 2>/dev/null; then
    echo "✅ Gunicorn module found with python3"
    GUNICORN_CMD="python3 -m gunicorn"
else
    echo "❌ Gunicorn not found, trying direct Python app run"
    python wsgi.py
    exit $?
fi

echo "✅ Setup complete. Starting Gunicorn..."

# Start the application with Gunicorn
exec $GUNICORN_CMD --bind 0.0.0.0:${PORT:-8000} wsgi:app \
    --workers 2 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
