# Configuration file for job scraper
# Environment-based configuration with production-ready defaults

import os
from typing import List

# Search Keywords
SEARCH_KEYWORDS: List[str] = [
    'python developer',
    'data scientist',
    'machine learning engineer',
    'software engineer',
    'DevOps engineer',
    'frontend developer',
    'backend developer',
    'full stack developer'
]

# Locations
LOCATIONS = {
    'USA': 'United States',
    'UK': 'United Kingdom',
    'Remote': 'Remote'
}

# Scraping settings (with environment variable overrides)
HEADLESS_MODE: bool = os.getenv('HEADLESS_MODE', 'True').lower() == 'true'
MAX_PAGES_PER_KEYWORD: int = int(os.getenv('MAX_PAGES_PER_KEYWORD', '3'))
MAX_JOBS_GLASSDOOR: int = int(os.getenv('MAX_JOBS_GLASSDOOR', '20'))

# Default location
DEFAULT_LOCATION: str = os.getenv('DEFAULT_LOCATION', 'United States')

# Output settings
OUTPUT_FILE: str = os.getenv('OUTPUT_FILE', 'jobs_output.json')

# API Configuration
API_PORT: int = int(os.getenv('PORT', '8080'))
API_DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
API_HOST: str = os.getenv('HOST', '0.0.0.0')

# Logging Configuration
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

# Playwright Browser Configuration
PLAYWRIGHT_BROWSERS_PATH: str = os.getenv('PLAYWRIGHT_BROWSERS_PATH', '/ms-playwright')

# Performance Settings
GUNICORN_WORKERS: int = int(os.getenv('GUNICORN_WORKERS', '1'))
GUNICORN_THREADS: int = int(os.getenv('GUNICORN_THREADS', '2'))
GUNICORN_TIMEOUT: int = int(os.getenv('GUNICORN_TIMEOUT', '600'))

# Scraping Limits (to prevent abuse and timeouts)
MAX_KEYWORDS_PER_REQUEST: int = int(os.getenv('MAX_KEYWORDS_PER_REQUEST', '3'))
MAX_PAGES_PER_REQUEST: int = int(os.getenv('MAX_PAGES_PER_REQUEST', '5'))

# Platform-specific settings
PLATFORM_NAME: str = os.getenv('PLATFORM', 'DigitalOcean')
