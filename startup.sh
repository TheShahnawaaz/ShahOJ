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

# Generate secret key if not provided
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  WARNING: No SECRET_KEY environment variable set. Generating one..."
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "✅ Generated SECRET_KEY (set this in Azure App Settings for persistence)"
fi

# Use Azure's Python and pip paths
echo "📦 Installing production dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.prod.txt

echo "✅ Setup complete. Starting Gunicorn..."

# Start the application with Gunicorn using python module
python3 -m gunicorn --bind 0.0.0.0:$PORT wsgi:app \
    --workers 2 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info
