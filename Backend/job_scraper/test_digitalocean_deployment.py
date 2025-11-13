"""
DigitalOcean Deployment Test Script
Test deployed Job Scraper API on DigitalOcean App Platform

Usage:
    python test_digitalocean_deployment.py https://your-app.ondigitalocean.app
"""

import sys
import time
import requests
import json
from typing import Dict, Optional
from datetime import datetime


class DigitalOceanDeploymentTester:
    def __init__(self, base_url: str):
        """
        Initialize the tester with the deployed app URL
        
        Args:
            base_url: The base URL of your deployed app (e.g., https://your-app.ondigitalocean.app)
        """
        self.base_url = base_url.rstrip('/')
        self.results = []
        
    def print_header(self, text: str):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"✅ {text}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"❌ {text}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"ℹ️  {text}")
    
    def test_health_check(self) -> bool:
        """Test /health endpoint"""
        self.print_header("Testing Health Check Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_success(f"Health check passed (Status: {response.status_code})")
                self.print_info(f"Status: {data.get('status')}")
                self.print_info(f"Timestamp: {data.get('timestamp')}")
                
                # Check browser availability
                browser = data.get('browser', {})
                if browser.get('available'):
                    self.print_success(f"Browser: {browser.get('message')}")
                    self.print_info(f"Browser Path: {browser.get('path')}")
                else:
                    self.print_error(f"Browser: {browser.get('message')}")
                    return False
                
                # Check environment
                env = data.get('environment', {})
                self.print_info(f"Python Version: {env.get('python_version')}")
                self.print_info(f"Platform: {env.get('platform')}")
                self.print_info(f"Port: {env.get('port')}")
                
                return True
            else:
                self.print_error(f"Health check failed (Status: {response.status_code})")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_error(f"Health check request failed: {str(e)}")
            return False
    
    def test_root_endpoint(self) -> bool:
        """Test / root endpoint"""
        self.print_header("Testing Root Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_success(f"Root endpoint passed (Status: {response.status_code})")
                self.print_info(f"API Name: {data.get('name')}")
                self.print_info(f"Version: {data.get('version')}")
                self.print_info(f"Status: {data.get('status')}")
                
                # List endpoints
                endpoints = data.get('endpoints', {})
                print("\n  Available Endpoints:")
                for endpoint, description in endpoints.items():
                    print(f"    • {endpoint}: {description}")
                
                return True
            else:
                self.print_error(f"Root endpoint failed (Status: {response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_error(f"Root endpoint request failed: {str(e)}")
            return False
    
    def test_status_endpoint(self) -> bool:
        """Test /api/status endpoint"""
        self.print_header("Testing Status Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_success(f"Status endpoint passed (Status: {response.status_code})")
                self.print_info(f"Scraping Status: {data.get('status')}")
                self.print_info(f"Jobs Count: {data.get('jobs_count')}")
                
                if data.get('last_heartbeat'):
                    self.print_info(f"Last Heartbeat: {data.get('last_heartbeat')}")
                
                return True
            else:
                self.print_error(f"Status endpoint failed (Status: {response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_error(f"Status endpoint request failed: {str(e)}")
            return False
    
    def test_scraping(self, platform: str = "SimplyHired", keywords: list = None, pages: int = 1) -> bool:
        """Test /api/scrape-jobs endpoint"""
        self.print_header(f"Testing Scraping Endpoint - {platform}")
        
        if keywords is None:
            keywords = ["python developer"]
        
        payload = {
            "platform": platform,
            "keywords": keywords,
            "pages": pages,
            "location": "United States"
        }
        
        self.print_info(f"Request payload: {json.dumps(payload, indent=2)}")
        self.print_info("⏳ Scraping may take 30-90 seconds...")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/scrape-jobs",
                json=payload,
                timeout=180  # 3 minutes timeout
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_success(f"Scraping completed in {elapsed:.1f} seconds")
                self.print_info(f"Success: {data.get('success')}")
                self.print_info(f"Total Jobs: {data.get('total_jobs')}")
                self.print_info(f"Scraped At: {data.get('scraped_at')}")
                
                # Show sample jobs
                jobs = data.get('jobs', [])
                if jobs:
                    print("\n  Sample Jobs:")
                    for i, job in enumerate(jobs[:3], 1):
                        print(f"\n  Job {i}:")
                        print(f"    Title: {job.get('title')}")
                        print(f"    Company: {job.get('company')}")
                        print(f"    Location: {job.get('location')}")
                        print(f"    Type: {job.get('job_type')}")
                        print(f"    URL: {job.get('url')[:60]}...")
                
                return True
            else:
                self.print_error(f"Scraping failed (Status: {response.status_code})")
                print(f"Response: {response.text[:500]}")
                return False
                
        except requests.exceptions.Timeout:
            self.print_error("Scraping request timed out (>180 seconds)")
            self.print_info("Try reducing pages or keywords, or increase GUNICORN_TIMEOUT")
            return False
        except requests.exceptions.RequestException as e:
            self.print_error(f"Scraping request failed: {str(e)}")
            return False
    
    def run_all_tests(self, test_scraping: bool = True):
        """Run all tests"""
        print("\n" + "🚀 " * 20)
        print("  DigitalOcean Deployment Test Suite")
        print("  Testing URL:", self.base_url)
        print("  Started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("🚀 " * 20)
        
        results = {}
        
        # Test 1: Health Check
        results['health'] = self.test_health_check()
        time.sleep(1)
        
        # Test 2: Root Endpoint
        results['root'] = self.test_root_endpoint()
        time.sleep(1)
        
        # Test 3: Status Endpoint
        results['status'] = self.test_status_endpoint()
        time.sleep(1)
        
        # Test 4: Scraping (optional - takes longer)
        if test_scraping:
            results['scraping'] = self.test_scraping(
                platform="SimplyHired",
                keywords=["python developer"],
                pages=1
            )
        
        # Print summary
        self.print_header("Test Summary")
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        print(f"\n  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n  Individual Results:")
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"    • {test_name.title()}: {status}")
        
        if all(results.values()):
            self.print_success("\n🎉 All tests passed! Deployment is healthy.")
            return True
        else:
            self.print_error("\n⚠️  Some tests failed. Check the logs above.")
            return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("❌ Error: Please provide the deployed app URL")
        print("\nUsage:")
        print("  python test_digitalocean_deployment.py https://your-app.ondigitalocean.app")
        print("\nExample:")
        print("  python test_digitalocean_deployment.py https://job-scraper-api-xxxxx.ondigitalocean.app")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    # Optional: Skip scraping test (faster)
    test_scraping = True
    if len(sys.argv) > 2 and sys.argv[2] == "--no-scraping":
        test_scraping = False
        print("ℹ️  Skipping scraping test (--no-scraping flag)")
    
    # Create tester and run
    tester = DigitalOceanDeploymentTester(base_url)
    success = tester.run_all_tests(test_scraping=test_scraping)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
