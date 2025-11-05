"""
Pre-Deployment Verification Script
Checks if everything is ready for deployment
"""

import os
import sys
import subprocess
from pathlib import Path

print("="*60)
print("  JOB SCRAPER API - PRE-DEPLOYMENT VERIFICATION")
print("="*60)

errors = []
warnings = []
success = []

# Check 1: Required files exist
print("\n1. Checking required files...")
required_files = [
    'api.py',
    'Screp.py',
    'config.py',
    'requirement.txt',
    'render.yaml',
    'Procfile',
    'runtime.txt',
    '.env.example',
    '.gitignore',
]

for file in required_files:
    if os.path.exists(file):
        success.append(f"✅ {file} exists")
    else:
        errors.append(f"❌ {file} is missing")

# Check 2: Documentation files
print("\n2. Checking documentation files...")
doc_files = [
    'README.md',
    'README_API.md',
    'QUICKSTART.md',
    'DEPLOYMENT.md',
    'PACKAGE_SUMMARY.md',
]

for file in doc_files:
    if os.path.exists(file):
        success.append(f"✅ {file} exists")
    else:
        warnings.append(f"⚠️  {file} is missing (optional but recommended)")

# Check 3: Test files
print("\n3. Checking test files...")
test_files = [
    'test_api.py',
    'n8n_workflow_example.json',
]

for file in test_files:
    if os.path.exists(file):
        success.append(f"✅ {file} exists")
    else:
        warnings.append(f"⚠️  {file} is missing (optional)")

# Check 4: Python dependencies
print("\n4. Checking Python dependencies...")
try:
    import flask
    success.append("✅ Flask is installed")
except ImportError:
    errors.append("❌ Flask is not installed (run: pip install -r requirement.txt)")

try:
    import flask_cors
    success.append("✅ Flask-CORS is installed")
except ImportError:
    errors.append("❌ Flask-CORS is not installed (run: pip install -r requirement.txt)")

try:
    from playwright.async_api import async_playwright
    success.append("✅ Playwright is installed")
except ImportError:
    errors.append("❌ Playwright is not installed (run: pip install -r requirement.txt)")

# Check 5: Playwright browsers
print("\n5. Checking Playwright browsers...")
try:
    result = subprocess.run(
        ['playwright', 'install', '--dry-run', 'chromium'],
        capture_output=True,
        text=True,
        timeout=10
    )
    if 'chromium' in result.stdout.lower():
        success.append("✅ Playwright command available")
    else:
        warnings.append("⚠️  Chromium may not be installed (run: playwright install chromium)")
except Exception as e:
    warnings.append(f"⚠️  Could not check Playwright browsers: {str(e)}")

# Check 6: Git repository
print("\n6. Checking Git status...")
try:
    result = subprocess.run(
        ['git', 'status'],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        success.append("✅ Git repository initialized")
        
        # Check for uncommitted changes
        if 'nothing to commit' in result.stdout:
            success.append("✅ All changes committed")
        else:
            warnings.append("⚠️  You have uncommitted changes")
    else:
        warnings.append("⚠️  Not a git repository")
except Exception as e:
    warnings.append(f"⚠️  Could not check Git status: {str(e)}")

# Check 7: Environment file
print("\n7. Checking environment configuration...")
if os.path.exists('.env'):
    success.append("✅ .env file exists (for local development)")
else:
    warnings.append("⚠️  .env file not found (optional, only needed for local overrides)")

if os.path.exists('.env.example'):
    success.append("✅ .env.example exists")

# Check 8: Configuration values
print("\n8. Checking configuration...")
try:
    with open('requirement.txt', 'r') as f:
        content = f.read()
        if 'flask' in content.lower():
            success.append("✅ Flask in requirement.txt")
        else:
            errors.append("❌ Flask not in requirement.txt")
        
        if 'playwright' in content.lower():
            success.append("✅ Playwright in requirement.txt")
        else:
            errors.append("❌ Playwright not in requirement.txt")
except Exception as e:
    errors.append(f"❌ Could not read requirement.txt: {str(e)}")

# Check 9: API file structure
print("\n9. Checking API code...")
try:
    with open('api.py', 'r') as f:
        content = f.read()
        
        if 'POST /api/scrape-jobs' in content or '/api/scrape-jobs' in content:
            success.append("✅ Main endpoint defined")
        else:
            errors.append("❌ Main endpoint not found in api.py")
        
        if 'from flask import' in content:
            success.append("✅ Flask imports present")
        else:
            errors.append("❌ Flask imports missing in api.py")
        
        if 'from Screp import JobScraper' in content:
            success.append("✅ JobScraper import present")
        else:
            errors.append("❌ JobScraper import missing in api.py")
except Exception as e:
    errors.append(f"❌ Could not read api.py: {str(e)}")

# Print Results
print("\n" + "="*60)
print("  VERIFICATION RESULTS")
print("="*60)

if success:
    print("\n✅ SUCCESS:")
    for item in success:
        print(f"  {item}")

if warnings:
    print("\n⚠️  WARNINGS:")
    for item in warnings:
        print(f"  {item}")

if errors:
    print("\n❌ ERRORS (Must fix before deployment):")
    for item in errors:
        print(f"  {item}")

# Summary
print("\n" + "="*60)
if errors:
    print("  ❌ VERIFICATION FAILED")
    print("="*60)
    print("\nPlease fix the errors above before deploying.")
    print("\nQuick fixes:")
    print("  1. Install dependencies: pip install -r requirement.txt")
    print("  2. Install Playwright: playwright install chromium")
    print("  3. Ensure all required files exist")
    sys.exit(1)
else:
    print("  ✅ VERIFICATION PASSED")
    print("="*60)
    if warnings:
        print("\n⚠️  There are warnings, but you can proceed with deployment.")
        print("Consider fixing warnings for optimal setup.")
    else:
        print("\n🎉 Everything looks great!")
    
    print("\n📋 Next Steps:")
    print("  1. Test locally: python api.py")
    print("  2. Run tests: python test_api.py")
    print("  3. Commit changes: git add . && git commit -m 'Add API'")
    print("  4. Push to GitHub: git push origin main")
    print("  5. Deploy to Render following DEPLOYMENT.md")
    print("\n📖 Read QUICKSTART.md for detailed instructions")
    sys.exit(0)
