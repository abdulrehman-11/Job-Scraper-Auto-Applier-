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
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.getenv(
    'PLAYWRIGHT_BROWSERS_PATH', 
    '/opt/render/project/src/browsers'
)

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
    Run the job scraper with specified parameters (MEMORY OPTIMIZED)
    
    This function uses sequential scraping to stay within 512 MB memory limit.
    Platforms are scraped one at a time with browser cleanup between each.
    
    Args:
        platform: Platform to scrape (SimplyHired, Talent.com) or None/all for both
        keywords: List of job search keywords
        pages: Number of pages to scrape per keyword (max 2 recommended for free tier)
        location: Job location
    
    Returns:
        Dictionary with success status and jobs data
    """
    global scraping_progress
    
    try:
        # Default parameters
        if keywords is None:
            keywords = ['python developer', 'react developer']
        
        # Limit to reasonable values for Render free tier (512 MB)
        # Recommended: 2 keywords, 2 pages = ~200-250 MB peak memory
        pages = min(pages, 2)  # Max 2 pages for free tier
        keywords = keywords[:2]  # Max 2 keywords for free tier
        
        logger.info(f"🚀 Starting scraper - Platform: {platform}, Keywords: {keywords}, Pages: {pages}, Location: {location}")
        logger.info(f"💾 Memory optimization: Sequential scraping enabled")
        
        # Initialize scraper (headless=True for production, False for local debugging)
        # Set DEBUG=true in environment to see browser window
        is_debug = os.getenv('DEBUG', 'false').lower() == 'true'
        headless_mode = not is_debug  # If DEBUG=true, headless=False (visible browser)
        
        if is_debug:
            logger.info("🐛 DEBUG mode: Browser will be VISIBLE")
        
        scraper = JobScraper(headless=headless_mode)
        
        # Update progress
        scraping_progress['status'] = 'running'
        scraping_progress['jobs_count'] = 0
        scraping_progress['last_heartbeat'] = datetime.now().isoformat()
        
        # Start heartbeat thread
        heartbeat_thread = Thread(target=heartbeat_logger, args=(300,), daemon=True)
        heartbeat_thread.start()
        
        # Scrape based on platform parameter
        if platform is None or platform.lower() == 'all':
            logger.info("📋 Scraping all platforms SEQUENTIALLY (SimplyHired → Talent.com)")
            
            # Use the new sequential scraper method
            await scraper.scrape_all_platforms_sequential(
                keywords=keywords,
                location=location,
                max_pages=pages,
                platform_timeout=150  # 2.5 min per platform
            )
            
            scraping_progress['jobs_count'] = len(scraper.jobs)
            logger.info(f"✅ Sequential scraping completed: {len(scraper.jobs)} total jobs")
        
        elif platform.lower() == 'simplyhired':
            logger.info("📋 Scraping SimplyHired only")
            await scraper.scrape_simplyhired(
                keywords=keywords,
                location=location,
                max_pages=pages
            )
            scraping_progress['jobs_count'] = len(scraper.jobs)
        
        elif platform.lower() in ['talent', 'talent.com']:
            logger.info("📋 Scraping Talent.com only")
            await scraper.scrape_talent(
                keywords=keywords,
                location=location,
                max_pages=pages
            )
            scraping_progress['jobs_count'] = len(scraper.jobs)
        
        else:
            raise ValueError(f"Unknown platform: {platform}. Use 'all', 'simplyhired', or 'talent'")
        
        # Process results (deduplication + filtering)
        logger.info("🔄 Processing results: removing duplicates and filtering...")
        scraper.remove_duplicates()
        scraper.filter_last_24_hours()
        
        # Get jobs and format for n8n
        jobs = scraper.get_jobs()
        scraped_at = datetime.now().isoformat()
        
        # Update progress
        scraping_progress['status'] = 'completed'
        scraping_progress['jobs_count'] = len(jobs)
        scraping_progress['last_heartbeat'] = scraped_at
        
        logger.info(f"✅ Scraping completed successfully: {len(jobs)} jobs after deduplication")
        
        return format_jobs_for_n8n(jobs, scraped_at)
    
    except Exception as e:
        scraping_progress['status'] = 'error'
        scraping_progress['last_heartbeat'] = datetime.now().isoformat()
        logger.error(f"❌ Scraping error: {str(e)}")
        raise


def check_browser_installation():
    """Check if Playwright browser is installed"""
    import subprocess
    try:
        browser_path = os.getenv('PLAYWRIGHT_BROWSERS_PATH', '/opt/render/project/src/browsers')
        
        # Check if browser directory exists
        if os.path.exists(browser_path):
            return {
                'available': True,
                'path': browser_path,
                'message': 'Browser directory found'
            }
        
        # Try to check with playwright
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
            'message': 'Browser not found'
        }
    except Exception as e:
        return {
            'available': False,
            'path': 'unknown',
            'message': f'Error checking browser: {str(e)}'
        }


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render with browser verification"""
    browser_status = check_browser_installation()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'scraping_status': scraping_progress['status'],
        'browser': browser_status,
        'environment': {
            'playwright_path': os.getenv('PLAYWRIGHT_BROWSERS_PATH', 'not set'),
            'python_version': os.sys.version.split()[0]
        }
    }), 200


@app.route('/api/scrape-jobs', methods=['POST'])
def scrape_jobs():
    """
    Main endpoint for scraping jobs (MEMORY OPTIMIZED FOR RENDER FREE TIER)
    
    Request body (all optional):
    {
        "platform": "all",  // or "simplyhired", "talent", null (defaults to "all")
        "keywords": ["python developer", "react developer"],  // max 2 recommended
        "pages": 2,  // max 2 recommended for 512 MB limit
        "location": "United States"
    }
    
    Response format:
    {
        "success": true,
        "total_jobs": 180,
        "scraped_at": "2025-11-13T00:05:00.000000",
        "jobs": [
            {
                "job_id": "abc123",
                "title": "Python Developer",
                "company": "TechCorp",
                "location": "Remote",
                "url": "https://...",
                "description": "Full job description...",
                "posted_date": "2025-11-12T10:30:00",
                "source": "SimplyHired",
                "fetched_at": "2025-11-13T00:05:00"
            },
            ...
        ]
    }
    
    Memory optimization:
    - Sequential scraping (one platform at a time)
    - Browser cleanup between platforms
    - Max 2 keywords, 2 pages recommended
    - Peak memory: ~400-450 MB
    """
    try:
        # Log request
        logger.info("📨 Received scrape request")
        
        # Parse request body (optional)
        data = request.get_json() or {}
        
        platform = data.get('platform', 'all')  # Default to 'all'
        keywords = data.get('keywords', ['python developer', 'react developer'])
        pages = data.get('pages', 2)  # Default 2 pages for free tier
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
        
        # Warn if exceeding recommended limits
        if len(keywords) > 2:
            logger.warning(f"⚠️  {len(keywords)} keywords requested (recommended: 2 for free tier)")
        if pages > 2:
            logger.warning(f"⚠️  {pages} pages requested (recommended: 2 for free tier)")
        
        # Log parameters
        logger.info(f"Parameters - Platform: {platform}, Keywords: {keywords}, Pages: {pages}, Location: {location}")
        logger.info(f"💾 Memory mode: Sequential scraping enabled")
        
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
    
    # Check browser installation on startup
    logger.info("🔍 Checking browser installation...")
    browser_status = check_browser_installation()
    if browser_status.get('chromium'):
        logger.info("✅ Chromium browser ready")
    else:
        logger.warning("⚠️  Chromium not found - scraping may fail!")
        logger.info("Run: playwright install chromium")
    
    logger.info(f"🚀 Starting Flask server on port {port}")
    logger.info(f"📍 API endpoint: http://localhost:{port}/api/scrape-jobs")
    logger.info(f"💡 Test with: curl -X POST http://localhost:{port}/api/scrape-jobs -H 'Content-Type: application/json' -d '{{\"keywords\":[\"python\"],\"pages\":1}}'")
    
    
    logger.info(f"🚀 Starting Job Scraper API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
