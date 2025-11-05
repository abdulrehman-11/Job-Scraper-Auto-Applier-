"""
Multi-Platform Job Scraper using Playwright
Supports: SimplyHired, Glassdoor, Talent.com
Optimized for daily scraping of tech jobs (last 24 hours)
WITH FULL JOB DESCRIPTIONS
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
import random
import hashlib

import logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class JobScraper:
    def __init__(self, headless: bool = False):
        """
        Initialize the job scraper
        
        Args:
            headless: Run browser in headless mode (True for production, False for debugging)
        """
        self.headless = headless
        self.jobs = []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
    
    def generate_job_id(self, title: str, company: str, source: str) -> str:
        """Generate unique job ID based on title and company (cross-platform)"""
        # Remove source from hash to detect duplicates across platforms
        unique_string = f"{company}_{title}".lower().strip()
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def generate_unique_key(self, title: str, company: str) -> str:
        """Generate key for duplicate detection"""
        # Normalize text for better matching
        title_clean = re.sub(r'[^\w\s]', '', title.lower().strip())
        company_clean = re.sub(r'[^\w\s]', '', company.lower().strip())
        return f"{company_clean}||{title_clean}"
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,;:()\-$€£¥]', '', text)
        return text.strip()
    
    def parse_posted_date(self, date_text: str) -> str:
        """Convert relative date to ISO format"""
        try:
            if not date_text:
                print(f"    ⚠️ Empty date text, using current date")
                return datetime.now().isoformat()
                
            date_text = date_text.lower().strip()
            now = datetime.now()
            
            # Remove "last updated:" prefix if present
            if 'last updated:' in date_text:
                date_text = date_text.replace('last updated:', '').strip()
            
            # Debug: Print what we're parsing
            print(f"    🔍 Parsing date: '{date_text[:100]}'")  # Limit to 100 chars for display
            
            # Check if text is too long (likely not a date)
            if len(date_text) > 100:
                print(f"    ⚠️ Text too long to be a date ({len(date_text)} chars), using current date")
                return now.isoformat()

            # Just posted / Today
            if 'just posted' in date_text or 'today' in date_text:
                print(f"    ✅ Parsed: just posted")
                return now.isoformat()
            
            # Yesterday
            if 'yesterday' in date_text or date_text == '1d':
                calculated_date = now - timedelta(days=1)
                print(f"    ✅ Parsed: yesterday -> {calculated_date.strftime('%Y-%m-%d')}")
                return calculated_date.isoformat()
            
            # Minutes ago (check before hours because 'min' might contain 'm')
            minutes_match = re.search(r'(\d+)\s*(?:minute|minutes|min|m)(?:\s+ago)?', date_text)
            if minutes_match:
                minutes = int(minutes_match.group(1))
                calculated_date = now - timedelta(minutes=minutes)
                print(f"    ✅ Parsed: {minutes} minutes ago -> {calculated_date.strftime('%Y-%m-%d %H:%M')}")
                return calculated_date.isoformat()
            
            # Hours ago - FIXED to include "hr" format
            hours_match = re.search(r'(\d+)\s*(?:hour|hours|hr|h)(?:\s+ago)?', date_text)
            if hours_match:
                hours = int(hours_match.group(1))
                calculated_date = now - timedelta(hours=hours)
                print(f"    ✅ Parsed: {hours} hours ago -> {calculated_date.strftime('%Y-%m-%d %H:%M')}")
                return calculated_date.isoformat()
            
            # Days ago (most common format: "2d", "3 days ago", etc.)
            days_match = re.search(r'(\d+)\s*(?:day|days|d)(?:\s+ago)?', date_text)
            if days_match:
                days = int(days_match.group(1))
                calculated_date = now - timedelta(days=days)
                print(f"    ✅ Parsed: {days} days ago -> {calculated_date.strftime('%Y-%m-%d')}")
                return calculated_date.isoformat()
            
            # Weeks ago
            weeks_match = re.search(r'(\d+)\s*(?:week|weeks|w)(?:\s+ago)?', date_text)
            if weeks_match:
                weeks = int(weeks_match.group(1))
                calculated_date = now - timedelta(weeks=weeks)
                print(f"    ✅ Parsed: {weeks} weeks ago -> {calculated_date.strftime('%Y-%m-%d')}")
                return calculated_date.isoformat()
            
            # Months ago (approximate: 30 days per month)
            months_match = re.search(r'(\d+)\s*(?:month|months|mo)(?:\s+ago)?', date_text)
            if months_match:
                months = int(months_match.group(1))
                calculated_date = now - timedelta(days=months * 30)
                print(f"    ✅ Parsed: {months} months ago -> {calculated_date.strftime('%Y-%m-%d')}")
                return calculated_date.isoformat()
            
            # Special case: "0d" or "0h" means just posted
            if date_text in ['0d', '0h', '0hr', '0m', '0 days', '0 hours']:
                print(f"    ✅ Parsed: 0 time units (just posted)")
                return now.isoformat()
            
            # If nothing matched, log and return current date
            print(f"    ⚠️ Could not parse date: '{date_text[:50]}...', using current date")
            return now.isoformat()

        except Exception as e:
            print(f"    ⚠️ Date parsing error for '{date_text[:50] if date_text else 'None'}': {str(e)}")
            return datetime.now().isoformat()
    
    async def setup_page_context(self, browser: Browser) -> Page:
        """Setup browser context with anti-detection measures"""
        context = await browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # New York coords
            color_scheme='light',
            has_touch=False,
            is_mobile=False,
        )
        
        await context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        
        page = await context.new_page()
        return page
    
    async def extract_simplyhired_description(self, page: Page) -> str:
        """
        Extract full description from SimplyHired's right panel
        Based on actual HTML structure from screenshots
        """
        try:
            # Wait for panel to load
            await asyncio.sleep(3)
            
            # From the HTML images, the structure is:
            # <aside aria-label="Job Title">
            #   <div class="css-1u3q0w0 scroll">  <- Scrollable content
            #     <div class="css-10747oj">       <- Main content wrapper
            #       ... all the job details ...
            
            all_text = ""
            
            # Strategy 1: Get entire aside content (most reliable)
            try:
                aside = await page.query_selector('aside[class*="css-"]')
                if aside:
                    # Get the scrollable div inside
                    scroll_div = await aside.query_selector('div[class*="scroll"]')
                    if scroll_div:
                        all_text = await scroll_div.inner_text()
                        if all_text and len(all_text) > 300:
                            print(f"        ✅ Got full description from scroll div: {len(all_text)} chars")
                            return all_text.strip()
                    
                    # Fallback: get from aside directly
                    all_text = await aside.inner_text()
                    if all_text and len(all_text) > 300:
                        print(f"        ✅ Got full description from aside: {len(all_text)} chars")
                        return all_text.strip()
            except Exception as e:
                print(f"        ⚠️ Strategy 1 failed: {str(e)}")
            
            # Strategy 2: Try by tabindex attribute (from HTML: div tabindex="0" class="css-1u3q0w0 scroll")
            try:
                scroll_div = await page.query_selector('div[tabindex="0"][class*="scroll"]')
                if scroll_div:
                    all_text = await scroll_div.inner_text()
                    if all_text and len(all_text) > 300:
                        print(f"        ✅ Got description from tabindex scroll div: {len(all_text)} chars")
                        return all_text.strip()
            except Exception as e:
                print(f"        ⚠️ Strategy 2 failed: {str(e)}")
            
            # Strategy 3: Get by specific class pattern
            try:
                content_div = await page.query_selector('div.css-10747oj')
                if content_div:
                    all_text = await content_div.inner_text()
                    if all_text and len(all_text) > 300:
                        print(f"        ✅ Got description from content div: {len(all_text)} chars")
                        return all_text.strip()
            except Exception as e:
                print(f"        ⚠️ Strategy 3 failed: {str(e)}")
            
            # Strategy 4: Try data-testid approach
            try:
                body_container = await page.query_selector('div[data-testid="viewJobBodyContainer"]')
                if body_container:
                    all_text = await body_container.inner_text()
                    if all_text and len(all_text) > 300:
                        print(f"        ✅ Got description from body container: {len(all_text)} chars")
                        return all_text.strip()
            except Exception as e:
                print(f"        ⚠️ Strategy 4 failed: {str(e)}")
            
            # If we got something but it's short, still return it
            if all_text:
                print(f"        ⚠️ Got short description: {len(all_text)} chars")
                return all_text.strip()
            
            print(f"        ❌ No description found with any strategy")
            return ""
            
        except Exception as e:
            print(f"        ❌ Error extracting description: {str(e)}")
            import traceback
            traceback.print_exc()
            return ""
    
    async def extract_talent_description(self, page: Page, job_url: str) -> Dict:
        """
        Extract full description from Talent.com by opening in new tab
        Returns dict with description and other details
        """
        try:
            context = page.context
            detail_page = await context.new_page()
            
            await detail_page.goto(job_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(random.uniform(2, 3))
            
            # Extract full description
            full_description = ""
            
            # Selectors based on your screenshot
            description_selectors = [
                'div.sc-fcd630a4-10.sc-fcd630a4-11.sc-6cde2aa1-10.cgBMEk.iroSSa.bEMPBB',
                'div[class*="fcd630a4"]',
                'div[class*="cgBMEk"]',
                'span[class*="sc-fcd630a4-15"]',
            ]
            
            for selector in description_selectors:
                try:
                    desc_elem = await detail_page.query_selector(selector)
                    if desc_elem:
                        full_description = await desc_elem.inner_text()
                        if len(full_description) > 100:  # Valid description
                            break
                except:
                    continue
            
            # If still not found, try getting all text content
            if not full_description or len(full_description) < 100:
                try:
                    # Get the main content area
                    main_content = await detail_page.query_selector('article, main, div[class*="jobcard"]')
                    if main_content:
                        full_description = await main_content.inner_text()
                except:
                    pass
            
            await detail_page.close()
            
            return {
                'full_description': full_description.strip()
            }
            
        except Exception as e:
            print(f"        ❌ Error opening detail page: {str(e)}")
            try:
                await detail_page.close()
            except:
                pass
            return {'full_description': ""}
    
    # ==================== SIMPLYHIRED SCRAPER ====================
    async def scrape_simplyhired(self, keywords: List[str], location: str = "USA", max_pages: int = 5):
        """Scrape SimplyHired with FULL descriptions from right panel"""
        print("\n" + "="*60)
        print("🔄 SCRAPING SIMPLYHIRED (WITH FULL DESCRIPTIONS)")
        print("="*60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            
            for keyword in keywords:
                print(f"\n📌 Searching for: '{keyword}'")
                
                try:
                    page = await self.setup_page_context(browser)
                    
                    query = keyword.replace(' ', '+')
                    url = f"https://www.simplyhired.com/search?q={query}&l={location}&t=1"
                    
                    print(f"  📄 Loading search results...")
                    await page.goto(url, wait_until='networkidle', timeout=60000)
                    await asyncio.sleep(random.uniform(3, 5))
                    
                    for page_num in range(1, max_pages + 1):
                        try:
                            await page.wait_for_selector('h2[data-testid="searchSerpJobTitle"]', timeout=10000)
                            await asyncio.sleep(2)
        
                            # CLOSE POPUP IF IT APPEARS
                            try:
                                close_button = await page.query_selector('button[data-testid="cta-closeModal"]')
                                if not close_button:
                                    close_button = await page.query_selector('div[class*="sc-4e5e0f9c-0"] button')

                                if close_button:
                                    is_visible = await close_button.is_visible()
                                    if is_visible:
                                        print(f"  🚫 Closing popup...")
                                        await close_button.click()
                                        await asyncio.sleep(1)
                            except Exception as e:
                                pass

                            job_cards = await page.query_selector_all('div[data-testid="searchSerpJob"]')
                            print(f"  📄 Page {page_num}: Found {len(job_cards)} jobs")
                            
                            for idx, card in enumerate(job_cards):
                                try:
                                    title_elem = await card.query_selector('h2[data-testid="searchSerpJobTitle"] a')
                                    title = await title_elem.inner_text() if title_elem else None
                                    job_url = await title_elem.get_attribute('href') if title_elem else None
                                    
                                    if job_url and not job_url.startswith('http'):
                                        job_url = f"https://www.simplyhired.com{job_url}"
                                    
                                    if not title:
                                        continue
                                    
                                    company_elem = await card.query_selector('span[data-testid="companyName"]')
                                    if not company_elem:
                                        text_elems = await card.query_selector_all('p.chakra-text')
                                        company = "Unknown"
                                        for elem in text_elems:
                                            text = await elem.inner_text()
                                            if "—" in text:
                                                company = text.split("—")[0].strip()
                                                break
                                    else:
                                        company = await company_elem.inner_text()
                                    
                                    location_elem = await card.query_selector('span[data-testid="searchSerpJobLocation"]')
                                    if not location_elem:
                                        location_elem = await card.query_selector('p.chakra-text.css-1sawo7p')
                                    job_location = await location_elem.inner_text() if location_elem else location
                                    
                                    salary_elem = await card.query_selector('p[data-testid="searchSerpJobSalaryConfirmed"]')
                                    salary = "Not specified"
                                    if salary_elem:
                                        salary = await salary_elem.inner_text()
                                    
                                    date_elem = await card.query_selector('p[data-testid="searchSerpJobDateStamp"]')
                                    if not date_elem:
                                        date_elem = await card.query_selector('span.css-5yilgw')
                                    posted_date_text = await date_elem.inner_text() if date_elem else None
                                    
                                    # Debug: Print what we extracted
                                    if posted_date_text:
                                        print(f"      📅 Date text found: '{posted_date_text}'")
                                    else:
                                        print(f"      ⚠️ No date element found, using default (just posted)")
                                        posted_date_text = "just posted"
                                    
                                    posted_date = self.parse_posted_date(posted_date_text)
                                    
                                    # SHORT description from listing (as fallback)
                                    desc_elem = await card.query_selector('p[data-testid="searchSerpJobSnippet"]')
                                    if not desc_elem:
                                        desc_elem = await card.query_selector('p.chakra-text.css-jhqp7z')
                                    short_description = await desc_elem.inner_text() if desc_elem else ""
                                    
                                    # NOW CLICK THE JOB TO LOAD DESCRIPTION IN RIGHT PANEL
                                    print(f"    📝 Job {idx + 1}: {title[:50]}...")
                                    
                                    try:
                                        # Click the job title to load details in right panel
                                        await title_elem.click()
                                        await asyncio.sleep(2)  # Wait for right panel to load
                                        
                                        # Try to get more accurate date from detail panel
                                        # data-testid="viewJobBodyPostingTimestamp" in the detail view
                                        try:
                                            detail_date_elem = await page.query_selector('span[data-testid="viewJobBodyPostingTimestamp"]')
                                            if detail_date_elem:
                                                detail_date_text = await detail_date_elem.inner_text()
                                                if detail_date_text and len(detail_date_text) < 50:
                                                    posted_date_text = detail_date_text
                                                    print(f"      📅 Detail date found: '{posted_date_text}'")
                                                    posted_date = self.parse_posted_date(posted_date_text)
                                        except:
                                            pass
                                        
                                        # Extract FULL description from right panel
                                        full_description = await self.extract_simplyhired_description(page)
                                        
                                        if full_description and len(full_description) > len(short_description):
                                            description = full_description
                                            print(f"      ✅ Got full description ({len(full_description)} chars)")
                                        else:
                                            description = short_description
                                            print(f"      ⚠️ Using short description ({len(short_description)} chars)")
                                    
                                    except Exception as e:
                                        print(f"      ⚠️ Could not get full description: {str(e)}")
                                        description = short_description
                                    
                                    if title and company:
                                        job_data = {
                                            'job_id': self.generate_job_id(title, company, 'SimplyHired'),
                                            'title': self.clean_text(title),
                                            'company': self.clean_text(company),
                                            'location': self.clean_text(job_location),
                                            'job_type': 'Full-time',
                                            'description': self.clean_text(description),
                                            'url': job_url,
                                            'posted_date': posted_date,
                                            'salary': self.clean_text(salary),
                                            'source': 'SimplyHired',
                                            'fetched_at': datetime.now().isoformat()
                                        }
                                        self.jobs.append(job_data)
                                    
                                    # Small delay between jobs
                                    await asyncio.sleep(random.uniform(0.5, 1))
                                                    
                                except Exception as e:
                                    print(f"      ❌ Error: {str(e)}")
                                    continue
                            
                            print(f"  ✅ Extracted {len(job_cards)} jobs from page {page_num}")
                            logging.info(f"SimplyHired: Extracted {len(job_cards)} jobs from page {page_num}")
                            
                            if page_num < max_pages:
                                next_button = await page.query_selector('a[data-testid="pageNumberBlockNext"]')
                                if not next_button:
                                    next_button = await page.query_selector('a.chakra-link.css-16mmgjw')
                                
                                if next_button:
                                    print(f"  ⏭️ Clicking next page...")
                                    await next_button.click()
                                    await asyncio.sleep(random.uniform(3, 5))
                                else:
                                    print(f"  ⏹️ No more pages available")
                                    break
                            
                        except Exception as e:
                            print(f"  ❌ Error on page {page_num}: {str(e)}")
                            break
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"  ❌ Error searching '{keyword}': {str(e)}")
                    continue
            
            await browser.close()
    
    # ==================== GLASSDOOR SCRAPER ====================
    async def scrape_glassdoor(self, keywords: List[str], location: str = "United States", max_loads: int = 5):
        """Scrape Glassdoor with Show More button clicking"""
        print("\n" + "="*60)
        print("🔄 SCRAPING GLASSDOOR")
        print("="*60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            )
            
            for keyword in keywords:
                print(f"\n📌 Searching for: '{keyword}'")
                
                try:
                    page = await self.setup_page_context(browser)
                    
                    query = keyword.replace(' ', '-')
                    location_formatted = location.replace(' ', '-').lower()
                    url = f"https://www.glassdoor.com/Job/{location_formatted}-{query}-jobs-SRCH_IL.0,13_IN1_KO14,31.htm?fromAge=1"

                    await page.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['en-US', 'en']
                        });
                    """)
                    
                    print(f"  📄 Loading: {url}")
                    await page.goto('https://www.glassdoor.com', wait_until='networkidle', timeout=60000)
                    await asyncio.sleep(random.uniform(3, 5))

                    await page.goto(url, wait_until='networkidle', timeout=60000)
                    await asyncio.sleep(random.uniform(6, 9))

                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight / 4)')
                    await asyncio.sleep(random.uniform(1, 2))
                    
                    content = await page.content()
                    if 'captcha' in content.lower() or 'blocked' in content.lower():
                        print("  ⚠️ CAPTCHA/Block detected!")
                        if not self.headless:
                            print("  ⏸️  Please solve CAPTCHA manually in the browser")
                            print("  Press Enter when done...")
                            input()
                            content = await page.content()
                            if 'captcha' in content.lower() or 'blocked' in content.lower():
                                print("  ❌ Still blocked, skipping Glassdoor")
                                await page.close()
                                continue
                        else:
                            print("  ❌ Skipping Glassdoor (run with headless=False to solve CAPTCHA)")
                            await page.close()
                            continue
                    
                    loads = 0
                    while loads < max_loads:
                        loads += 1
                        
                        try:
                            await page.wait_for_selector('li[data-test="jobListing"]', timeout=10000)
                            await asyncio.sleep(2)
                        except:
                            print(f"  ⚠️ No job listings found")
                            break
                        
                        job_cards = await page.query_selector_all('li[data-test="jobListing"]')
                        print(f"  📄 Load {loads}: Found {len(job_cards)} total jobs")
                        
                        for card in job_cards:
                            try:
                                data_jobid = await card.get_attribute('data-jobid')
                                if any(job.get('job_id', '').endswith(data_jobid or '') for job in self.jobs):
                                    continue
                                
                                title_elem = await card.query_selector('a[data-test="job-title"]')
                                if not title_elem:
                                    title_elem = await card.query_selector('a.JobCard_jobTitle__GLyJ1')
                                title = await title_elem.inner_text() if title_elem else None
                                job_url = await title_elem.get_attribute('href') if title_elem else None
                                
                                if job_url and not job_url.startswith('http'):
                                    job_url = f"https://www.glassdoor.com{job_url}"
                                
                                if not title:
                                    continue
                                
                                company_elem = await card.query_selector('span[data-test="employer-name"]')
                                if not company_elem:
                                    company_elem = await card.query_selector('div.EmployerProfile_profileContainer__28h9t span')
                                company = await company_elem.inner_text() if company_elem else "Unknown"
                                
                                location_elem = await card.query_selector('div[data-test="emp-location"]')
                                if not location_elem:
                                    location_elem = await card.query_selector('div.JobCard_location__Ds1fM')
                                job_location = await location_elem.inner_text() if location_elem else location
                                
                                salary_elem = await card.query_selector('div[data-test="detailSalary"]')
                                if not salary_elem:
                                    salary_elem = await card.query_selector('div.JobCard_salaryEstimate__OpbTW')
                                salary = await salary_elem.inner_text() if salary_elem else "Not specified"
                                
                                desc_elem = await card.query_selector('div[data-test="descSnippet"]')
                                if not desc_elem:
                                    desc_elem = await card.query_selector('div.JobCard_jobDescriptionSnippet__l1tnl')
                                description = await desc_elem.inner_text() if desc_elem else ""
                                
                                if title and company:
                                    job_data = {
                                        'job_id': self.generate_job_id(title, company, f'Glassdoor-{data_jobid}'),
                                        'title': self.clean_text(title),
                                        'company': self.clean_text(company),
                                        'location': self.clean_text(job_location),
                                        'job_type': 'Full-time',
                                        'description': self.clean_text(description),
                                        'url': job_url,
                                        'posted_date': datetime.now().isoformat(),
                                        'salary': self.clean_text(salary),
                                        'source': 'Glassdoor',
                                        'fetched_at': datetime.now().isoformat()
                                    }
                                    self.jobs.append(job_data)
                            
                            except Exception as e:
                                continue
                        
                        if loads < max_loads:
                            try:
                                show_more = await page.query_selector('button:has-text("Show more jobs")')
                                if not show_more:
                                    show_more = await page.query_selector('button.button_Button__o_a9q')
                                
                                if show_more:
                                    is_visible = await show_more.is_visible()
                                    if is_visible:
                                        print(f"  ⏬ Clicking 'Show more jobs'...")
                                        await show_more.click()
                                        await asyncio.sleep(random.uniform(3, 5))
                                    else:
                                        print(f"  ⏹️ No more jobs to load")
                                        break
                                else:
                                    print(f"  ⏹️ Show more button not found")
                                    break
                            except Exception as e:
                                print(f"  ⚠️ Could not load more jobs: {str(e)}")
                                break
                    
                    print(f"  ✅ Total extracted: {loads} loads")
                    logging.info(f"Glassdoor: Extracted jobs from {loads} loads")
                    await page.close()
                    await asyncio.sleep(random.uniform(5, 8))
                    
                except Exception as e:
                    print(f"  ❌ Error: {str(e)}")
                    continue
            
            await browser.close()
    
    # ==================== TALENT.COM SCRAPER ====================
    async def scrape_talent(self, keywords: List[str], location: str = "USA", max_pages: int = 5):
        """Scrape Talent.com with FULL descriptions (opens new tab)"""
        print("\n" + "="*60)
        print("🔄 SCRAPING TALENT.COM (WITH FULL DESCRIPTIONS)")
        print("="*60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            
            for keyword in keywords:
                print(f"\n📌 Searching for: '{keyword}'")
                
                try:
                    page = await self.setup_page_context(browser)
                    
                    query = keyword.replace(' ', '-')
                    url = f"https://www.talent.com/jobs?k={query}&l={location}&date=1"
                    
                    print(f"  📄 Loading search results...")
                    await page.goto(url, wait_until='networkidle', timeout=60000)
                    await asyncio.sleep(random.uniform(4, 6))
                    
                    for page_num in range(1, max_pages + 1):
                        try:
                            await page.wait_for_selector('section[data-testid^="jobcard-container"]', timeout=10000)
                            await asyncio.sleep(2)
                            
                            job_cards = await page.query_selector_all('section[data-testid^="jobcard-container"]')
                            print(f"  📄 Page {page_num}: Found {len(job_cards)} jobs")
                            
                            for idx, card in enumerate(job_cards):
                                try:
                                    title_elem = await card.query_selector('h2[color="#30183F"]')
                                    if not title_elem:
                                        title_elem = await card.query_selector('h2.sc-fcd630a4-20')
                                    title = await title_elem.inner_text() if title_elem else None

                                    link_elem = await card.query_selector('a[href*="/view?id="]')
                                    if not link_elem:
                                        link_elem = await card.query_selector('a.sc-d93925ca-5')
                                    job_url = await link_elem.get_attribute('href') if link_elem else None

                                    if job_url and not job_url.startswith('http'):
                                        job_url = f"https://www.talent.com{job_url}"

                                    if not title or not job_url:
                                        continue
                                    
                                    company_elem = await card.query_selector('span[color="#691F74"]')
                                    if not company_elem:
                                        company_elem = await card.query_selector('span.sc-fcd630a4-12')
                                    company = await company_elem.inner_text() if company_elem else "Unknown"

                                    location_elem = await card.query_selector('span[color="#222222"]')
                                    if not location_elem:
                                        location_elem = await card.query_selector('span.sc-fcd630a4-11')
                                    job_location = await location_elem.inner_text() if location_elem else location

                                    # FIXED: Talent.com date is in a specific span with class pattern
                                    # Looking for the "Last updated: X day ago" text in the card header
                                    date_elem = None
                                    try:
                                        # Try multiple selectors for the date element
                                        # The date is usually in a span near the top of the card
                                        date_elem = await card.query_selector('span.sc-fcd630a4-5:has-text("ago")')
                                        if not date_elem:
                                            date_elem = await card.query_selector('span.sc-fcd630a4-6:has-text("ago")')
                                        if not date_elem:
                                            # Try to find any span containing "day ago" or "hour ago"
                                            all_spans = await card.query_selector_all('span')
                                            for span in all_spans:
                                                span_text = await span.inner_text()
                                                if 'ago' in span_text.lower() or 'day' in span_text.lower() or 'hour' in span_text.lower():
                                                    # Check if it's actually a date (short text)
                                                    if len(span_text) < 50:  # Date text should be short
                                                        date_elem = span
                                                        break
                                    except:
                                        pass
                                    
                                    posted_date_text = await date_elem.inner_text() if date_elem else None
                                    
                                    # Debug: Print what we extracted
                                    if posted_date_text:
                                        print(f"      📅 Date text found: '{posted_date_text}'")
                                    else:
                                        print(f"      ⚠️ No date element found, using default (just posted)")
                                        posted_date_text = "just posted"
                                    
                                    posted_date = self.parse_posted_date(posted_date_text)

                                    salary = "Not specified"
                                    all_text = await card.inner_text()
                                    if "$" in all_text:
                                        salary_match = re.search(r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*(?:per|/)\s*(?:hour|year|annum))?', all_text)
                                        if salary_match:
                                            salary = salary_match.group(0)

                                    # SHORT description from listing (as fallback)
                                    desc_elem = await card.query_selector('span[class*="sc-fcd630a4-5"]')
                                    short_description = await desc_elem.inner_text() if desc_elem else ""
                                    short_description = short_description.split("Show more")[0].strip()

                                    # NOW OPEN NEW TAB TO GET FULL DESCRIPTION
                                    print(f"    📝 Job {idx + 1}: {title[:50]}...")
                                    
                                    try:
                                        full_details = await self.extract_talent_description(page, job_url)
                                        
                                        if full_details and full_details['full_description'] and len(full_details['full_description']) > len(short_description):
                                            description = full_details['full_description']
                                            print(f"      ✅ Got full description ({len(description)} chars)")
                                        else:
                                            description = short_description
                                            print(f"      ⚠️ Using short description ({len(short_description)} chars)")
                                    
                                    except Exception as e:
                                        print(f"      ⚠️ Could not get full description: {str(e)}")
                                        description = short_description

                                    if title and company:
                                        job_data = {
                                            'job_id': self.generate_job_id(title, company, 'Talent'),
                                            'title': self.clean_text(title),
                                            'company': self.clean_text(company),
                                            'location': self.clean_text(job_location),
                                            'job_type': 'Full-time',
                                            'description': self.clean_text(description),
                                            'url': job_url,
                                            'posted_date': posted_date,
                                            'salary': self.clean_text(salary),
                                            'source': 'Talent.com',
                                            'fetched_at': datetime.now().isoformat()
                                        }
                                        self.jobs.append(job_data)
                                    
                                    # Small delay between jobs
                                    await asyncio.sleep(random.uniform(1, 2))

                                except Exception as e:
                                    print(f"      ❌ Error: {str(e)}")
                                    continue
                            
                            print(f"  ✅ Extracted {len(job_cards)} jobs from page {page_num}")
                            logging.info(f"Talent.com: Extracted {len(job_cards)} jobs from page {page_num}")
                            
                            if page_num < max_pages:
                                # Look for next page link in pagination nav
                                next_button = None
                                pagination = await page.query_selector('nav.sc-5ec0130d-0')
                                if not pagination:
                                    pagination = await page.query_selector('nav[class*="eRQgGg"]')

                                if pagination:
                                    # Find the link with title="2", "3", etc. or the next arrow
                                    all_links = await pagination.query_selector_all('a')
                                    for link in all_links:
                                        title_attr = await link.get_attribute('title')
                                        if title_attr and title_attr.isdigit() and int(title_attr) == page_num + 1:
                                            next_button = link
                                            break
                                        
                                    # If not found, look for arrow/svg indicating next
                                    if not next_button:
                                        for link in all_links:
                                            svg = await link.query_selector('svg')
                                            if svg:
                                                # Check if it's the "next" arrow (usually the last one)
                                                next_button = link
                                                break
                                
                                if next_button:
                                    print(f"  ⏭️ Clicking next page...")
                                    
                                    # Get the href and clean it
                                    href = await next_button.get_attribute('href')
                                    if href and 'showSignInModal=true' in href:
                                        # Remove the popup trigger
                                        href = href.replace('&showSignInModal=true', '').replace('showSignInModal=true&', '')
                                        await page.goto(f"https://www.talent.com{href}", wait_until='networkidle', timeout=60000)
                                    else:
                                        await next_button.click()
                                    
                                    await asyncio.sleep(random.uniform(3, 5))
                                else:
                                    print(f"  ⏹️ No more pages available")
                                    break
                            
                        except Exception as e:
                            print(f"  ❌ Error on page {page_num}: {str(e)}")
                            break
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"  ❌ Error searching '{keyword}': {str(e)}")
                    continue
            
            await browser.close()
    
    # ==================== UTILITY METHODS ====================
    def remove_duplicates(self):
        """Remove duplicate jobs based on company + title, keep most recent"""
        unique_jobs = {}

        for job in self.jobs:
            # Create unique key from company + title
            key = self.generate_unique_key(job.get('title', ''), job.get('company', ''))

            if key not in unique_jobs:
                # First occurrence - add it
                unique_jobs[key] = job
            else:
                # Duplicate found - keep the more recent one
                try:
                    existing_date = datetime.fromisoformat(unique_jobs[key]['posted_date'].replace('Z', ''))
                    new_date = datetime.fromisoformat(job['posted_date'].replace('Z', ''))

                    if new_date > existing_date:
                        # New job is more recent, replace
                        unique_jobs[key] = job
                except:
                    # If date parsing fails, keep first occurrence
                    pass
                
        removed = len(self.jobs) - len(unique_jobs)
        self.jobs = list(unique_jobs.values())
        print(f"\n🗑️  Removed {removed} duplicate jobs (same title + company)")

    def remove_duplicates_from_existing(self, filename: str = 'jobs_output.json'):
        """Remove jobs that already exist in the output file (unless reposted after 24h)"""
        try:
            # Load existing jobs
            existing_jobs = []
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # Only parse if file has content
                    data = json.loads(content)
                    existing_jobs = data.get('jobs', [])
            
            if not existing_jobs:
                print(f"📄 No existing jobs found in {filename}")
                return
            
            # Create lookup dict: key -> (job, posted_date)
            existing_lookup = {}
            for job in existing_jobs:
                key = self.generate_unique_key(job.get('title', ''), job.get('company', ''))
                try:
                    posted_date = datetime.fromisoformat(job['posted_date'].replace('Z', ''))
                    existing_lookup[key] = (job, posted_date)
                except:
                    existing_lookup[key] = (job, None)
            
            # Filter new jobs
            filtered_jobs = []
            removed_count = 0
            
            for job in self.jobs:
                key = self.generate_unique_key(job.get('title', ''), job.get('company', ''))
                
                if key not in existing_lookup:
                    # Completely new job
                    filtered_jobs.append(job)
                else:
                    # Job exists - check if it's a repost (24h+ difference)
                    existing_job, existing_date = existing_lookup[key]
                    
                    try:
                        new_date = datetime.fromisoformat(job['posted_date'].replace('Z', ''))
                        
                        if existing_date and new_date:
                            time_diff = new_date - existing_date
                            
                            if time_diff.total_seconds() >= 24 * 3600:  # 24 hours
                                # Reposted after 24h - keep it
                                filtered_jobs.append(job)
                                print(f"  ♻️ Repost detected: {job['title'][:40]}... at {job['company'][:20]}...")
                            else:
                                # Same job within 24h - skip
                                removed_count += 1
                        else:
                            # Can't determine date - skip to be safe
                            removed_count += 1
                            
                    except Exception as e:
                        # Date parsing error - skip this job
                        removed_count += 1
            
            self.jobs = filtered_jobs
            print(f"🔄 Compared with existing jobs: Removed {removed_count} already-scraped jobs")
            
        except FileNotFoundError:
            print(f"📄 No existing file found ({filename}), keeping all jobs")
        except Exception as e:
            print(f"⚠️ Error loading existing jobs: {str(e)}")
    
    def filter_last_24_hours(self):
        """Filter jobs to only include those from last 24 hours"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        filtered = []
        
        for job in self.jobs:
            try:
                job_date = datetime.fromisoformat(job['posted_date'].replace('Z', ''))
                if job_date >= cutoff_time:
                    filtered.append(job)
            except:
                filtered.append(job)
        
        removed = len(self.jobs) - len(filtered)
        self.jobs = filtered
        print(f"⏰ Filtered to last 24 hours: Removed {removed} old jobs")
    
    def save_to_json(self, filename: str = 'jobs_output.json'):
        """Save jobs to JSON file, merging with existing jobs"""
        # Load existing jobs
        existing_jobs = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # Only parse if file has content
                    data = json.loads(content)
                    existing_jobs = data.get('jobs', [])
                else:
                    print(f"📄 File {filename} is empty, starting fresh")
        except FileNotFoundError:
            print(f"📄 No existing file found, creating new {filename}")
        except json.JSONDecodeError as e:
            print(f"⚠️ Invalid JSON in {filename}, starting fresh. Error: {str(e)}")
        except Exception as e:
            print(f"⚠️ Error loading existing jobs: {str(e)}, starting fresh")
        
        # Merge: existing + new jobs
        all_jobs = existing_jobs + self.jobs

        data = {
            'scraped_at': datetime.now().isoformat(),
            'total_jobs': len(all_jobs),
            'new_jobs_added': len(self.jobs),
            'jobs': all_jobs
        }

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved {len(self.jobs)} NEW jobs (Total: {len(all_jobs)} jobs in {filename})")
        except Exception as e:
            print(f"❌ Error saving to {filename}: {str(e)}")
    
    def get_stats(self):
        """Print scraping statistics"""
        sources = {}
        for job in self.jobs:
            source = job.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print("\n" + "="*60)
        print("📊 SCRAPING SUMMARY")
        print("="*60)
        print(f"Total Jobs Scraped: {len(self.jobs)}")
        print(f"\nBy Source:")
        for source, count in sources.items():
            print(f"  • {source}: {count} jobs")
        print("="*60)
    
    def get_jobs(self) -> List[Dict]:
        """Return the scraped jobs"""
        return self.jobs


# ==================== MAIN EXECUTION ====================
async def main():
    """Main execution function"""
    
    SEARCH_KEYWORDS = [
        'python developer',
        'data scientist', 
        'machine learning engineer',
        'software engineer',
        'full stack developer'
    ]
    
    LOCATION = 'United States'
    
    scraper = JobScraper(headless=False)
    
    print("🚀 Starting Multi-Platform Job Scraper (WITH FULL DESCRIPTIONS)")
    print(f"📅 Target: Jobs from last 24 hours")
    print(f"🔍 Keywords: {', '.join(SEARCH_KEYWORDS[:3])}...")
    print(f"📍 Location: {LOCATION}\n")
    
    #print("\n🎯 PHASE 1: SimplyHired")
    #await scraper.scrape_simplyhired(
    #    keywords=SEARCH_KEYWORDS[:2],
    #    location=LOCATION,
    #    max_pages=5
    #)
    
    print("\n🎯 PHASE 2: Talent.com")
    await scraper.scrape_talent(
        keywords=SEARCH_KEYWORDS[:2],
        location=LOCATION,
        max_pages=5
    )
    
    #print("\n🎯 PHASE 3: Glassdoor")
    #await scraper.scrape_glassdoor(
    #    keywords=SEARCH_KEYWORDS[:1],
    #    location=LOCATION,
    #    max_loads=5
    #)
    
    # Remove duplicates within newly scraped jobs
    scraper.remove_duplicates()
    
    # Filter to last 24 hours
    scraper.filter_last_24_hours()
    
    # Remove jobs that already exist in file (unless reposted after 24h)
    scraper.remove_duplicates_from_existing('jobs_output.json')
    
    # Save to file (merges with existing)
    scraper.save_to_json('jobs_output.json')
    scraper.get_stats()
    
    print("\n✅ Scraping completed successfully!")
    
    return scraper.get_jobs()


if __name__ == "__main__":
    jobs = asyncio.run(main())
    
    print("\n📄 Sample Jobs (first 3):")
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Posted: {job['posted_date'][:10]}")
        print(f"   Description Length: {len(job['description'])} characters")
        print(f"   Source: {job['source']}")
        print(f"   URL: {job['url']}")