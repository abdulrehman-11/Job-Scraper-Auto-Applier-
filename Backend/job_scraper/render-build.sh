#!/usr/bin/env bash
# Render build script for Job Scraper API

set -e  # Exit on error

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirement.txt

echo "🎭 Installing Playwright browsers to persistent location..."
# Set browser path to persistent storage (not cache)
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/browsers
echo "Browser installation path: $PLAYWRIGHT_BROWSERS_PATH"

# Install chromium to the persistent location
playwright install chromium

# Verify installation
echo "🔍 Verifying browser installation..."
if [ -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    echo "✅ Browser directory exists at: $PLAYWRIGHT_BROWSERS_PATH"
    ls -la "$PLAYWRIGHT_BROWSERS_PATH" || true
else
    echo "⚠️ Warning: Browser directory not found at expected location"
fi

echo "✅ Build completed successfully!"
