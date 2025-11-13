# Production-ready Dockerfile for DigitalOcean App Platform
# Multi-stage build for optimized image size and security

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies required for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core dependencies
    wget \
    gnupg \
    ca-certificates \
    # Playwright browser dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libxshmfence1 \
    # Additional dependencies for stability
    fonts-liberation \
    libappindicator3-1 \
    libu2f-udev \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirement.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirement.txt

# Install Playwright and browsers
# Set browser path to a writable location in the container
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN pip install playwright==1.40.0 && \
    playwright install chromium
    
# Install Playwright dependencies manually (avoid deprecated packages issue)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Additional Playwright runtime dependencies
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /ms-playwright

# Switch to non-root user
USER appuser

# Expose port (DigitalOcean will set PORT environment variable)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()"

# Default environment variables (can be overridden in DigitalOcean)
ENV PORT=8080 \
    DEBUG=False \
    HEADLESS_MODE=True \
    MAX_PAGES_PER_KEYWORD=3 \
    DEFAULT_LOCATION="United States" \
    LOG_LEVEL=INFO

# Start application with gunicorn
# Use shell form to allow environment variable substitution
CMD gunicorn --bind 0.0.0.0:${PORT} \
    --workers 1 \
    --threads 2 \
    --timeout 600 \
    --keep-alive 5 \
    --log-level ${LOG_LEVEL} \
    --access-logfile - \
    --error-logfile - \
    api:app
