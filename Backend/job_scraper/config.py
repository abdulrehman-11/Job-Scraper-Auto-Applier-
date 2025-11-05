# Configuration file for job scraper

SEARCH_KEYWORDS = [
    'python developer',
    'data scientist',
    'machine learning engineer',
    'software engineer',
    'DevOps engineer',
    'frontend developer',
    'backend developer',
    'full stack developer'
]

LOCATIONS = {
    'USA': 'United States',
    'UK': 'United Kingdom',
    'Remote': 'Remote'
}

# Scraping settings
HEADLESS_MODE = False  # Set to True for production
MAX_PAGES_PER_KEYWORD = 2
MAX_JOBS_GLASSDOOR = 20

# Output settings
OUTPUT_FILE = 'jobs_output.json'