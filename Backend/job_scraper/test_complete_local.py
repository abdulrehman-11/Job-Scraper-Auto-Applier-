"""
Complete Local Testing Script for Job Scraper API
Alternative to Postman - runs all tests with progress tracking

Usage:
    python test_complete_local.py
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8080"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def test_health_check() -> bool:
    """Test health endpoint"""
    print_header("Test 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Browser Available: {data.get('browser', {}).get('available')}")
            print_info(f"Python Version: {data.get('environment', {}).get('python_version')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_api_info() -> bool:
    """Test root endpoint"""
    print_header("Test 2: API Information")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("API info retrieved")
            print_info(f"Name: {data.get('name')}")
            print_info(f"Version: {data.get('version')}")
            print_info(f"Status: {data.get('status')}")
            return True
        else:
            print_error(f"API info failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API info error: {str(e)}")
        return False

def test_status() -> bool:
    """Test status endpoint"""
    print_header("Test 3: Status Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Status check passed")
            print_info(f"Scraping Status: {data.get('status')}")
            print_info(f"Jobs Count: {data.get('jobs_count')}")
            return True
        else:
            print_error(f"Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Status check error: {str(e)}")
        return False

def test_quick_scrape() -> bool:
    """Test quick scraping (1 page, 1 keyword)"""
    print_header("Test 4: Quick Scrape (1 page, ~2 minutes)")
    
    payload = {
        "platform": "SimplyHired",
        "keywords": ["python developer"],
        "pages": 1,
        "location": "United States"
    }
    
    print_info("Starting quick scrape...")
    print_info("Payload: " + json.dumps(payload, indent=2))
    print_warning("This will take 30-90 seconds...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/scrape-jobs",
            json=payload,
            timeout=180  # 3 minutes
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Quick scrape completed in {elapsed:.1f} seconds")
            print_info(f"Total Jobs: {data.get('total_jobs')}")
            print_info(f"Success: {data.get('success')}")
            
            # Show sample job
            if data.get('jobs') and len(data['jobs']) > 0:
                job = data['jobs'][0]
                print(f"\n{Colors.OKBLUE}Sample Job:{Colors.ENDC}")
                print(f"  Title: {job.get('title')}")
                print(f"  Company: {job.get('company')}")
                print(f"  Location: {job.get('location')}")
                print(f"  Posted: {job.get('posted_date')}")
            
            return True
        else:
            print_error(f"Quick scrape failed: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print_error("Quick scrape timed out (>3 minutes)")
        return False
    except Exception as e:
        print_error(f"Quick scrape error: {str(e)}")
        return False

def test_medium_scrape() -> bool:
    """Test medium scraping (2 pages, 2 keywords, single platform)"""
    print_header("Test 5: Medium Scrape (2 pages, 2 keywords, ~15-20 min)")
    
    payload = {
        "platform": "SimplyHired",
        "keywords": ["python developer", "data scientist"],
        "pages": 2,
        "location": "United States"
    }
    
    print_info("Starting medium scrape test...")
    print_info("Payload: " + json.dumps(payload, indent=2))
    print_warning("This will take 15-20 minutes...")
    print_info("You can monitor progress at: http://localhost:8080/api/status")
    print_info("Or check Docker logs: docker logs -f job-scraper-api")
    
    response = input("\nProceed with medium scrape? (y/n): ")
    
    if response.lower() != 'y':
        print_warning("Skipping medium scrape test")
        return True  # Don't fail the test suite
    
    try:
        start_time = time.time()
        print_info(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
        
        response = requests.post(
            f"{BASE_URL}/api/scrape-jobs",
            json=payload,
            timeout=1800  # 30 minutes
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Medium scrape completed in {elapsed/60:.1f} minutes")
            print_info(f"Total Jobs: {data.get('total_jobs')}")
            print_info(f"Success: {data.get('success')}")
            return True
        else:
            print_error(f"Medium scrape failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print_error("Medium scrape timed out (>30 minutes)")
        return False
    except Exception as e:
        print_error(f"Medium scrape error: {str(e)}")
        return False

def test_full_scrape() -> bool:
    """Test full production scraping (all platforms, 3 keywords, 3 pages)"""
    print_header("Test 6: Full Scrape (ALL PLATFORMS, ~60 min)")
    
    payload = {
        "platform": "all",
        "keywords": ["python developer", "data scientist", "machine learning engineer"],
        "pages": 3,
        "location": "United States"
    }
    
    print_info("Starting FULL PRODUCTION scrape test...")
    print_info("Payload: " + json.dumps(payload, indent=2))
    print_warning("This will take 30-60 minutes!")
    print_info("Monitor at: http://localhost:8080/api/status")
    print_info("Docker logs: docker logs -f job-scraper-api")
    
    response = input("\nProceed with FULL scrape? (y/n): ")
    
    if response.lower() != 'y':
        print_warning("Skipping full scrape test")
        return True
    
    try:
        start_time = time.time()
        start_datetime = datetime.now()
        print_info(f"Started at: {start_datetime.strftime('%H:%M:%S')}")
        print_info("Grab a coffee ☕ - this will take a while...")
        
        # Monitor progress in separate thread would be nice, but keeping simple
        print_info("\nTip: Open another terminal and run:")
        print_info("  docker logs -f job-scraper-api")
        print_info("\nWaiting for response...\n")
        
        response = requests.post(
            f"{BASE_URL}/api/scrape-jobs",
            json=payload,
            timeout=3600  # 1 hour
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"FULL scrape completed in {elapsed/60:.1f} minutes!")
            print_info(f"Total Jobs: {data.get('total_jobs')}")
            print_info(f"Success: {data.get('success')}")
            print_info(f"Scraped At: {data.get('scraped_at')}")
            
            # Save results to file
            output_file = f"scrape_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print_success(f"Results saved to: {output_file}")
            
            return True
        else:
            print_error(f"Full scrape failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print_error("Full scrape timed out (>1 hour)")
        return False
    except Exception as e:
        print_error(f"Full scrape error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}  Job Scraper API - Complete Local Test Suite{Colors.ENDC}")
    print(f"{Colors.BOLD}  Testing URL: {BASE_URL}{Colors.ENDC}")
    print(f"{Colors.BOLD}  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    results = {}
    
    # Phase 1: Basic tests (quick)
    print_info("PHASE 1: Basic Validation (< 1 minute)")
    results['health'] = test_health_check()
    time.sleep(1)
    
    results['api_info'] = test_api_info()
    time.sleep(1)
    
    results['status'] = test_status()
    time.sleep(1)
    
    # Phase 2: Quick scrape test
    print_info("\nPHASE 2: Quick Scrape Test (~2 minutes)")
    results['quick_scrape'] = test_quick_scrape()
    time.sleep(2)
    
    # Phase 3: Medium scrape (optional)
    print_info("\nPHASE 3: Medium Scrape Test (optional, ~15-20 minutes)")
    results['medium_scrape'] = test_medium_scrape()
    
    # Phase 4: Full scrape (optional)
    print_info("\nPHASE 4: Full Production Scrape (optional, ~60 minutes)")
    results['full_scrape'] = test_full_scrape()
    
    # Summary
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"{Colors.OKGREEN}Passed: {passed}{Colors.ENDC}")
    print(f"{Colors.FAIL}Failed: {failed}{Colors.ENDC}")
    print(f"Success Rate: {(passed/total)*100:.1f}%\n")
    
    print("Individual Results:")
    for test_name, result in results.items():
        status = f"{Colors.OKGREEN}✅ PASSED{Colors.ENDC}" if result else f"{Colors.FAIL}❌ FAILED{Colors.ENDC}"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    if all(results.values()):
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed! Ready for DigitalOcean deployment!{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}⚠️  Some tests failed. Review errors above.{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
