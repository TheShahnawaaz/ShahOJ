#!/usr/bin/env python3
"""
Production runner for PocketOJ - GUARANTEED NO RESTARTS
Use this for local production testing
"""
import os
import sys
from pathlib import Path

# Force production configuration
os.environ['POCKETOJ_CONFIG'] = 'config.prod.yaml'
os.environ['FLASK_ENV'] = 'production'

# Add project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import config
from app import app

def main():
    """Run Flask in production mode with zero restart risk"""
    
    # Verify production settings
    if config.get('web.debug', True):
        print("❌ ERROR: Debug mode is enabled! Check config.prod.yaml")
        sys.exit(1)
    
    # Get configuration
    host = config.get('web.host', '0.0.0.0')
    port = config.get('web.port', 8000)
    
    print("🚀 Starting PocketOJ in PRODUCTION mode")
    print("=====================================")
    print(f"📊 Debug mode: {config.get('web.debug', 'undefined')}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📁 Problems dir: {config.get('system.problems_dir', 'problems')}")
    print("⚠️  AUTO-RELOAD: DISABLED - Server will NOT restart when files change")
    print()
    
    # Run Flask with production settings
    app.run(
        host=host,
        port=port,
        debug=False,           # Force debug off
        use_reloader=False,    # CRITICAL: No auto-reload
        threaded=True,         # Enable threading
        processes=1            # Single process
    )

if __name__ == '__main__':
    main()
