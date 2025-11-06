#!/usr/bin/env bash
# Render build script for Job Scraper API

set -e  # Exit on error

echo "📦 Installing Python dependencies..."
pip install -r requirement.txt

echo "🎭 Installing Playwright browsers..."
# Install only chromium without system dependencies
playwright install chromium

echo "✅ Build completed successfully!"
