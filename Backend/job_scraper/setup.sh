#!/bin/bash
# Job Scraper API - Installation Script for Linux/Mac

echo "=========================================================="
echo "  JOB SCRAPER API - AUTOMATED SETUP"
echo "=========================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python installation
echo -e "${YELLOW}1. Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "   ${GREEN}✅ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "   ${RED}❌ Python not found. Please install Python 3.9+${NC}"
    exit 1
fi

# Check pip
echo ""
echo -e "${YELLOW}2. Checking pip...${NC}"
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "   ${GREEN}✅ pip found: $PIP_VERSION${NC}"
else
    echo -e "   ${RED}❌ pip not found. Please install pip${NC}"
    exit 1
fi

# Install Python packages
echo ""
echo -e "${YELLOW}3. Installing Python packages...${NC}"
echo -e "   ${CYAN}This may take 2-3 minutes...${NC}"
if pip3 install -r requirement.txt --quiet; then
    echo -e "   ${GREEN}✅ Python packages installed successfully${NC}"
else
    echo -e "   ${RED}❌ Failed to install Python packages${NC}"
    echo -e "   ${YELLOW}Try running: pip3 install -r requirement.txt${NC}"
    exit 1
fi

# Install Playwright browsers
echo ""
echo -e "${YELLOW}4. Installing Playwright browsers...${NC}"
echo -e "   ${CYAN}This may take 3-5 minutes (downloads Chromium ~200MB)...${NC}"
if playwright install chromium --with-deps; then
    echo -e "   ${GREEN}✅ Playwright browsers installed successfully${NC}"
else
    echo -e "   ${YELLOW}⚠️  Playwright browser installation may have issues${NC}"
    echo -e "   ${YELLOW}Try running manually: playwright install chromium${NC}"
fi

# Verify installation
echo ""
echo -e "${YELLOW}5. Verifying installation...${NC}"
python3 verify_setup.py || echo -e "   ${YELLOW}⚠️  Could not run verification script${NC}"

# Create .env file if it doesn't exist
echo ""
echo -e "${YELLOW}6. Setting up environment file...${NC}"
if [ -f ".env" ]; then
    echo -e "   ${GREEN}✅ .env file already exists${NC}"
else
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        echo -e "   ${GREEN}✅ Created .env from .env.example${NC}"
        echo -e "   ${CYAN}📝 You can edit .env to customize settings${NC}"
    else
        echo -e "   ${YELLOW}⚠️  .env.example not found, skipping${NC}"
    fi
fi

# Summary
echo ""
echo "=========================================================="
echo -e "  ${GREEN}✅ INSTALLATION COMPLETE${NC}"
echo "=========================================================="
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo ""
echo -e "${NC}1. Start the API:${NC}"
echo -e "   ${CYAN}python3 api.py${NC}"
echo ""
echo -e "${NC}2. Test the API (in another terminal):${NC}"
echo -e "   ${CYAN}python3 test_api.py${NC}"
echo ""
echo -e "${NC}3. Or test manually:${NC}"
echo -e "   ${CYAN}curl http://localhost:5000/health${NC}"
echo ""
echo -e "${NC}4. Read the quick start guide:${NC}"
echo -e "   ${CYAN}cat QUICKSTART.md${NC}"
echo ""
echo -e "${NC}5. When ready to deploy:${NC}"
echo -e "   ${CYAN}Follow DEPLOYMENT.md${NC}"
echo ""
echo "=========================================================="
