"""
Test script for Render deployed Job Scraper API
Tests health check, browser availability, and actual scraping
"""

import requests
import json
import time
from datetime import datetime

# Your deployed API URL
API_URL = "https://job-scraper-api-o5mm.onrender.com"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_health_check():
    """Test the health endpoint and browser availability"""
    print_section("TEST 1: Health Check & Browser Verification")
    
    try:
        print(f"📡 Calling: {API_URL}/health")
        response = requests.get(f"{API_URL}/health", timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Response:")
            print(json.dumps(data, indent=2))
            
            # Check browser availability
            if 'browser' in data:
                browser_status = data['browser']
                if browser_status.get('available'):
                    print("\n✅ Browser is AVAILABLE!")
                    print(f"   Path: {browser_status.get('path')}")
                else:
                    print("\n❌ Browser is NOT available!")
                    print(f"   Message: {browser_status.get('message')}")
                    return False
            
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (API might be cold starting, try again)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_root_endpoint():
    """Test the root endpoint for API info"""
    print_section("TEST 2: API Information")
    
    try:
        print(f"📡 Calling: {API_URL}/")
        response = requests.get(f"{API_URL}/", timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 API Info:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"⚠️ Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_scraping_small():
    """Test actual scraping with minimal parameters"""
    print_section("TEST 3: Small Scraping Test (1 page, 1 keyword)")
    
    try:
        print(f"📡 Calling: {API_URL}/api/scrape-jobs")
        print("\n📝 Request Body:")
        
        payload = {
            "platform": "SimplyHired",
            "keywords": ["python"],
            "pages": 1,
            "location": "United States"
        }
        
        print(json.dumps(payload, indent=2))
        
        print("\n⏳ Scraping in progress (this may take 1-3 minutes)...")
        print("   Render free tier might timeout after 30 seconds...")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{API_URL}/api/scrape-jobs",
                json=payload,
                timeout=120  # 2 minute timeout
            )
            
            elapsed = time.time() - start_time
            print(f"\n⏱️  Completed in {elapsed:.1f} seconds")
            
            print(f"✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print("\n📊 Scraping Results:")
                print(f"   Success: {data.get('success')}")
                print(f"   Total Jobs: {data.get('total_jobs')}")
                print(f"   Scraped At: {data.get('scraped_at')}")
                
                if data.get('jobs') and len(data['jobs']) > 0:
                    print(f"\n📄 Sample Job (First Result):")
                    first_job = data['jobs'][0]
                    print(f"   Title: {first_job.get('title')}")
                    print(f"   Company: {first_job.get('company')}")
                    print(f"   Location: {first_job.get('location')}")
                    print(f"   Job Type: {first_job.get('job_type')}")
                    print(f"   URL: {first_job.get('url')[:60]}...")
                    print(f"   Source: {first_job.get('source_api')}")
                    
                    print("\n✅ SCRAPING WORKS! Jobs retrieved successfully!")
                    return True
                else:
                    print("\n⚠️ No jobs found in response")
                    print(f"Full response: {json.dumps(data, indent=2)[:500]}")
                    return False
            else:
                print(f"\n❌ Error Status: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"\n❌ Request timed out after {elapsed:.1f} seconds")
            print("   This is likely due to Render free tier 30-second timeout")
            print("   Solutions:")
            print("   1. Upgrade to Render paid plan")
            print("   2. Use smaller scraping scope (already minimal)")
            print("   3. Implement async/webhook pattern")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_status_endpoint():
    """Test the status endpoint"""
    print_section("TEST 4: Scraping Status")
    
    try:
        print(f"📡 Calling: {API_URL}/api/status")
        response = requests.get(f"{API_URL}/api/status", timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Current Status:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"⚠️ Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "🚀"*35)
    print("  RENDER DEPLOYMENT TEST SUITE")
    print("  Testing: https://job-scraper-api-o5mm.onrender.com")
    print("  Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🚀"*35)
    
    results = {}
    
    # Test 1: Health Check
    results['health'] = test_health_check()
    time.sleep(1)
    
    # Test 2: Root Endpoint
    results['root'] = test_root_endpoint()
    time.sleep(1)
    
    # Test 3: Status Endpoint
    results['status'] = test_status_endpoint()
    time.sleep(1)
    
    # Test 4: Actual Scraping (only if health check passed)
    if results['health']:
        print("\n⚠️  WARNING: The next test will actually scrape jobs.")
        print("   This may take 1-3 minutes and might timeout on free tier.")
        print("   Press Enter to continue or Ctrl+C to skip...")
        try:
            input()
            results['scraping'] = test_scraping_small()
        except KeyboardInterrupt:
            print("\n⏭️  Skipping scraping test")
            results['scraping'] = None
    else:
        print("\n⏭️  Skipping scraping test (health check failed)")
        results['scraping'] = None
    
    # Summary
    print_section("TEST SUMMARY")
    
    total_tests = sum(1 for v in results.values() if v is not None)
    passed_tests = sum(1 for v in results.values() if v is True)
    
    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed\n")
    
    for test_name, result in results.items():
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"   {status} - {test_name.upper()}")
    
    print("\n" + "="*70)
    
    if results.get('health') and results.get('scraping'):
        print("\n🎉 SUCCESS! Your API is fully functional and ready for n8n!")
        print("\n📌 Next Steps:")
        print("   1. Use this URL in n8n HTTP Request node:")
        print(f"      {API_URL}/api/scrape-jobs")
        print("   2. Configure POST request with JSON body")
        print("   3. Set timeout to 600000ms (10 minutes)")
    elif results.get('health') and not results.get('scraping'):
        print("\n⚠️  API is running but scraping failed (likely timeout issue)")
        print("\n📌 Options:")
        print("   1. Upgrade Render to paid plan for longer timeout")
        print("   2. Reduce scraping scope (already minimal)")
        print("   3. Browser might not be installed correctly")
    else:
        print("\n❌ API has issues. Check the logs above for details.")
        print("\n📌 Debugging:")
        print("   1. Check Render dashboard logs")
        print("   2. Verify environment variables are set")
        print("   3. Ensure build completed successfully")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
