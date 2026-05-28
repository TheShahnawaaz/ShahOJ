#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Navigate to app directory
cd /home/ubuntu/PocketOJ

# Pull latest code
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Activate virtual environment and install dependencies
echo "🐍 Installing dependencies..."
source venv/bin/activate || source .venv/bin/activate
pip install -r requirements.txt

# Restart service
echo "🔄 Restarting PocketOJ systemd service..."
sudo systemctl restart pocketoj

echo "✅ Deployment finished successfully!"
