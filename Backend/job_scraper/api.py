"""
Job Scraper REST API for n8n Integration
Synchronous endpoint that returns scraped jobs in n8n format
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from threading import Thread
from typing import Dict, List, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS

from Screp import JobScraper

# Set Playwright browser path BEFORE any imports
# Support multiple deployment platforms (DigitalOcean, Render, Docker, etc.)
DEFAULT_BROWSER_PATHS = [
    '/ms-playwright',  # Docker container default
    '/opt/render/project/src/browsers',  # Render.com
    '/home/app/browsers',  # DigitalOcean custom
    os.path.expanduser('~/.cache/ms-playwright'),  # Local fallback
]

# Use environment variable or detect available path
playwright_browser_path = os.getenv('PLAYWRIGHT_BROWSERS_PATH')
if not playwright_browser_path:
    for path in DEFAULT_BROWSER_PATHS:
        if os.path.exists(path):
            playwright_browser_path = path
            break
    if not playwright_browser_path:
        playwright_browser_path = DEFAULT_BROWSER_PATHS[0]  # Default to Docker path

os.environ['PLAYWRIGHT_BROWSERS_PATH'] = playwright_browser_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for n8n

# Global variable to track scraping progress
scraping_progress = {
    'status': 'idle',
    'jobs_count': 0,
    'last_heartbeat': None
}


def heartbeat_logger(interval=300):
    """
    Send periodic heartbeat logs every 5 minutes during scraping
    This prevents Render from thinking the app is frozen
    """
    global scraping_progress
    
    while scraping_progress['status'] == 'running':
        time.sleep(interval)
        if scraping_progress['status'] == 'running':
            logger.info(f"🔄 Still scraping... processed {scraping_progress['jobs_count']} jobs")
            scraping_progress['last_heartbeat'] = datetime.now().isoformat()


def format_jobs_for_n8n(jobs: List[Dict], scraped_at: str) -> Dict:
    """
    Format scraped jobs to match n8n expected format
    
    Expected format:
    {
      "success": true,
      "total_jobs": 20,
      "scraped_at": "2025-11-04T22:30:00.000000",
      "jobs": [...]
    }
    """
    formatted_jobs = []
    
    for job in jobs:
        # Ensure all required fields are present
        formatted_job = {
            'job_id': job.get('job_id', ''),
            'title': job.get('title', ''),
            'company': job.get('company', ''),
            'location': job.get('location', ''),
            'job_type': job.get('job_type', 'Full-time'),
            'description': job.get('description', ''),
            'url': job.get('url', ''),
            'skills_required': job.get('skills_required', ''),
            'posted_date': job.get('posted_date', ''),
            'salary': job.get('salary', 'Not specified'),
            'source_api': job.get('source', ''),  # Map 'source' to 'source_api' for n8n
            'fetched_at': job.get('fetched_at', '')
        }
        formatted_jobs.append(formatted_job)
    
    return {
        'success': True,
        'total_jobs': len(formatted_jobs),
        'scraped_at': scraped_at,
        'jobs': formatted_jobs
    }


async def run_scraper(
    platform: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    pages: int = 1,
    location: str = "United States"
) -> Dict:
    """
    Run the job scraper with specified parameters
    
    Args:
        platform: Platform to scrape (SimplyHired, Glassdoor, Talent.com) or None for all
        keywords: List of job search keywords
        pages: Number of pages to scrape per keyword
        location: Job location
    
    Returns:
        Dictionary with success status and jobs data
    """
    global scraping_progress
    
    try:
        # Default parameters
        if keywords is None:
            keywords = ['python developer']
        
        # Limit to reasonable values to prevent timeout
        pages = min(pages, 5)  # Max 5 pages
        keywords = keywords[:3]  # Max 3 keywords
        
        logger.info(f"🚀 Starting scraper - Platform: {platform}, Keywords: {keywords}, Pages: {pages}, Location: {location}")
        
        # Initialize scraper (headless=True for production)
        scraper = JobScraper(headless=True)
        
        # Update progress
        scraping_progress['status'] = 'running'
        scraping_progress['jobs_count'] = 0
        
        # Start heartbeat thread
        heartbeat_thread = Thread(target=heartbeat_logger, args=(300,), daemon=True)
        heartbeat_thread.start()
        
        # Scrape based on platform
        if platform is None or platform.lower() == 'all':
            logger.info("📋 Scraping all platforms")
            
            # SimplyHired
            try:
                await scraper.scrape_simplyhired(
                    keywords=keywords,
                    location=location,
                    max_pages=pages
                )
                scraping_progress['jobs_count'] = len(scraper.jobs)
                logger.info(f"✅ SimplyHired: {len(scraper.jobs)} jobs")
            except Exception as e:
                logger.error(f"❌ SimplyHired error: {str(e)}")
            
            # Talent.com
            try:
                await scraper.scrape_talent(
                    keywords=keywords,
                    location=location,
                    max_pages=pages
                )
                scraping_progress['jobs_count'] = len(scraper.jobs)
                logger.info(f"✅ Talent.com: {len(scraper.jobs)} jobs")
            except Exception as e:
                logger.error(f"❌ Talent.com error: {str(e)}")
            
            # Glassdoor - DISABLED (uncomment to enable)
            # Note: Glassdoor often has CAPTCHA issues in headless mode
            # try:
            #     await scraper.scrape_glassdoor(
            #         keywords=keywords[:1],  # Only 1 keyword for Glassdoor
            #         location=location,
            #         max_loads=pages
            #     )
            #     scraping_progress['jobs_count'] = len(scraper.jobs)
            #     logger.info(f"✅ Glassdoor: {len(scraper.jobs)} jobs")
            # except Exception as e:
            #     logger.error(f"❌ Glassdoor error: {str(e)}")
        
        elif platform.lower() == 'simplyhired':
            await scraper.scrape_simplyhired(
                keywords=keywords,
                location=location,
                max_pages=pages
            )
            scraping_progress['jobs_count'] = len(scraper.jobs)
        
        elif platform.lower() == 'talent' or platform.lower() == 'talent.com':
            await scraper.scrape_talent(
                keywords=keywords,
                location=location,
                max_pages=pages
            )
            scraping_progress['jobs_count'] = len(scraper.jobs)
        
        elif platform.lower() == 'glassdoor':
            await scraper.scrape_glassdoor(
                keywords=keywords,
                location=location,
                max_loads=pages
            )
            scraping_progress['jobs_count'] = len(scraper.jobs)
        
        else:
            raise ValueError(f"Unknown platform: {platform}")
        
        # Process results
        scraper.remove_duplicates()
        scraper.filter_last_24_hours()
        
        # Get jobs and format for n8n
        jobs = scraper.get_jobs()
        scraped_at = datetime.now().isoformat()
        
        # Update progress
        scraping_progress['status'] = 'completed'
        scraping_progress['jobs_count'] = len(jobs)
        
        logger.info(f"✅ Scraping completed: {len(jobs)} jobs found")
        
        return format_jobs_for_n8n(jobs, scraped_at)
    
    except Exception as e:
        scraping_progress['status'] = 'error'
        logger.error(f"❌ Scraping error: {str(e)}")
        raise


def check_browser_installation():
    """Check if Playwright browser is installed - platform agnostic"""
    import subprocess
    try:
        # Get the configured browser path
        browser_path = os.getenv('PLAYWRIGHT_BROWSERS_PATH', '/ms-playwright')
        
        # Check if browser directory exists
        if os.path.exists(browser_path):
            # Check for chromium specifically
            chromium_dirs = [
                os.path.join(browser_path, 'chromium-*'),
                os.path.join(browser_path, 'chrome-*'),
            ]
            import glob
            for pattern in chromium_dirs:
                if glob.glob(pattern):
                    return {
                        'available': True,
                        'path': browser_path,
                        'message': 'Chromium browser found'
                    }
        
        # Try to check with playwright command
        result = subprocess.run(
            ['playwright', 'install', '--dry-run', 'chromium'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if 'already installed' in result.stdout.lower() or result.returncode == 0:
            return {
                'available': True,
                'path': browser_path,
                'message': 'Browser appears to be installed'
            }
        
        return {
            'available': False,
            'path': browser_path,
            'message': 'Browser not found - may need installation'
        }
    except Exception as e:
        return {
            'available': False,
            'path': browser_path if 'browser_path' in locals() else 'unknown',
            'message': f'Error checking browser: {str(e)}'
        }


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with browser verification - platform agnostic"""
    browser_status = check_browser_installation()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'scraping_status': scraping_progress['status'],
        'browser': browser_status,
        'environment': {
            'playwright_path': os.getenv('PLAYWRIGHT_BROWSERS_PATH', 'not set'),
            'python_version': os.sys.version.split()[0],
            'platform': 'DigitalOcean' if os.getenv('DIGITALOCEAN') else 'Generic',
            'port': os.getenv('PORT', '8080')
        }
    }), 200


@app.route('/api/scrape-jobs', methods=['POST'])
def scrape_jobs():
    """
    Main endpoint for scraping jobs
    
    Request body (all optional):
    {
        "platform": "SimplyHired",  // or "Glassdoor", "Talent.com", "all", null
        "keywords": ["python developer", "data scientist"],
        "pages": 1,
        "location": "United States"
    }
    
    Response format:
    {
        "success": true,
        "total_jobs": 20,
        "scraped_at": "2025-11-04T22:30:00.000000",
        "jobs": [...]
    }
    """
    try:
        # Log request
        logger.info("📨 Received scrape request")
        
        # Parse request body (optional)
        data = request.get_json() or {}
        
        platform = data.get('platform')
        keywords = data.get('keywords', ['python developer'])
        pages = data.get('pages', 1)
        location = data.get('location', 'United States')
        
        # Validate parameters
        if not isinstance(keywords, list) or len(keywords) == 0:
            return jsonify({
                'success': False,
                'error': 'keywords must be a non-empty list',
                'total_jobs': 0,
                'jobs': []
            }), 400
        
        if not isinstance(pages, int) or pages < 1:
            return jsonify({
                'success': False,
                'error': 'pages must be a positive integer',
                'total_jobs': 0,
                'jobs': []
            }), 400
        
        # Log parameters
        logger.info(f"Parameters - Platform: {platform}, Keywords: {keywords}, Pages: {pages}, Location: {location}")
        
        # Run scraper synchronously (this will block until complete)
        result = asyncio.run(run_scraper(
            platform=platform,
            keywords=keywords,
            pages=pages,
            location=location
        ))
        
        # Return results
        logger.info(f"✅ Returning {result['total_jobs']} jobs to client")
        return jsonify(result), 200
    
    except ValueError as e:
        # Validation error
        logger.error(f"❌ Validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'total_jobs': 0,
            'jobs': []
        }), 400
    
    except Exception as e:
        # Internal server error
        logger.error(f"❌ Server error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f"Internal server error: {str(e)}",
            'total_jobs': 0,
            'jobs': []
        }), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_progress), 200


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'name': 'Job Scraper API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/scrape-jobs': 'Scrape jobs from job boards',
            'GET /health': 'Health check',
            'GET /api/status': 'Get scraping status',
        },
        'status': 'running'
    }), 200


if __name__ == '__main__':
    # Development server
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting Job Scraper API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
