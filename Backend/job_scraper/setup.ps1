# Job Scraper API - Installation Script for Windows
# This script installs all dependencies and verifies the setup

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  JOB SCRAPER API - AUTOMATED SETUP" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "1. Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ Python found: $pythonVersion" -ForegroundColor Green
    
    # Check if version is 3.9+
    if ($pythonVersion -match "Python 3\.(\d+)") {
        $minorVersion = [int]$Matches[1]
        if ($minorVersion -lt 9) {
            Write-Host "   ⚠️  Warning: Python 3.9+ recommended, you have $pythonVersion" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ❌ Python not found. Please install Python 3.9+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check pip
Write-Host ""
Write-Host "2. Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "   ✅ pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ pip not found. Please install pip" -ForegroundColor Red
    exit 1
}

# Install Python packages
Write-Host ""
Write-Host "3. Installing Python packages..." -ForegroundColor Yellow
Write-Host "   This may take 2-3 minutes..." -ForegroundColor Cyan
try {
    pip install -r requirement.txt --quiet
    Write-Host "   ✅ Python packages installed successfully" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to install Python packages" -ForegroundColor Red
    Write-Host "   Try running: pip install -r requirement.txt" -ForegroundColor Yellow
    exit 1
}

# Install Playwright browsers
Write-Host ""
Write-Host "4. Installing Playwright browsers..." -ForegroundColor Yellow
Write-Host "   This may take 3-5 minutes (downloads Chromium ~200MB)..." -ForegroundColor Cyan
try {
    playwright install chromium --with-deps
    Write-Host "   ✅ Playwright browsers installed successfully" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Playwright browser installation may have issues" -ForegroundColor Yellow
    Write-Host "   Try running manually: playwright install chromium" -ForegroundColor Yellow
}

# Verify installation
Write-Host ""
Write-Host "5. Verifying installation..." -ForegroundColor Yellow
try {
    python verify_setup.py
} catch {
    Write-Host "   ⚠️  Could not run verification script" -ForegroundColor Yellow
}

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "6. Setting up environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✅ .env file already exists" -ForegroundColor Green
} else {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "   ✅ Created .env from .env.example" -ForegroundColor Green
        Write-Host "   📝 You can edit .env to customize settings" -ForegroundColor Cyan
    } else {
        Write-Host "   ⚠️  .env.example not found, skipping" -ForegroundColor Yellow
    }
}

# Summary
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ✅ INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Start the API:" -ForegroundColor White
Write-Host "   python api.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Test the API (in another terminal):" -ForegroundColor White
Write-Host "   python test_api.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Or test manually:" -ForegroundColor White
Write-Host "   Invoke-RestMethod -Uri 'http://localhost:5000/health' -Method GET" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Read the quick start guide:" -ForegroundColor White
Write-Host "   QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. When ready to deploy:" -ForegroundColor White
Write-Host "   Follow DEPLOYMENT.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
