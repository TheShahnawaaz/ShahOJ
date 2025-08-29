#!/bin/bash
# Azure App Service startup script for PocketOJ

echo "🚀 Starting PocketOJ on Azure App Service"
echo "========================================"

# Create necessary directories
mkdir -p /tmp/pocketoj
mkdir -p logs

# Set environment variables for production
export FLASK_ENV=production
export POCKETOJ_CONFIG=config.prod.yaml

# Generate secret key if not provided
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  WARNING: No SECRET_KEY environment variable set. Generating one..."
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
    echo "✅ Generated SECRET_KEY (set this in Azure App Settings for persistence)"
fi

# Install any missing dependencies (in case requirements weren't fully processed)
pip install -r requirements.prod.txt

echo "✅ Setup complete. Starting Gunicorn..."

# Start the application with Gunicorn (NO AUTO-RELOAD)
gunicorn --bind 0.0.0.0:$PORT wsgi:app \
    --workers 2 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --no-sendfile \
    --reuse-port
