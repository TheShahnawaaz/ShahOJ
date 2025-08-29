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

# Determine which Python command to use
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "❌ No Python interpreter found"
    exit 1
fi

echo "🐍 Using Python: $PYTHON_CMD ($(${PYTHON_CMD} --version 2>&1))"

# Generate secret key if not provided
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  WARNING: No SECRET_KEY environment variable set. Generating one..."
    export SECRET_KEY=$(${PYTHON_CMD} -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "dev-secret-key-$(date +%s)")
    echo "✅ Generated SECRET_KEY"
fi

echo "📦 Checking dependencies..."

# Verify gunicorn is available (try multiple methods)
if command -v gunicorn >/dev/null 2>&1; then
    echo "✅ Gunicorn command found"
    GUNICORN_CMD="gunicorn"
elif ${PYTHON_CMD} -c "import gunicorn" 2>/dev/null; then
    echo "✅ Gunicorn module found"
    GUNICORN_CMD="${PYTHON_CMD} -m gunicorn"
else
    echo "⚠️  Gunicorn not found, starting with Flask development server"
    echo "🔧 This might happen during first deployment while dependencies install"
    
    # Try to install gunicorn first
    echo "📦 Attempting to install gunicorn..."
    ${PYTHON_CMD} -m pip install gunicorn 2>/dev/null || true
    
    # Check again after installation attempt
    if ${PYTHON_CMD} -c "import gunicorn" 2>/dev/null; then
        echo "✅ Gunicorn installed successfully"
        GUNICORN_CMD="${PYTHON_CMD} -m gunicorn"
    else
        echo "🔄 Starting with direct Python app (Flask development server)"
        exec ${PYTHON_CMD} wsgi.py
    fi
fi

echo "✅ Setup complete. Starting application with: $GUNICORN_CMD"

# Start the application with Gunicorn
exec $GUNICORN_CMD --bind 0.0.0.0:${PORT:-8000} wsgi:app \
    --workers 2 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
