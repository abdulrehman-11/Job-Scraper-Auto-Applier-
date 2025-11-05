"""
Test script for Job Scraper API
Tests all endpoints locally before deployment
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_root():
    """Test root endpoint"""
    print_section("Test 1: Root Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        print("✅ Root endpoint works!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_health():
    """Test health check endpoint"""
    print_section("Test 2: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
        print("✅ Health check passed!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_status():
    """Test status endpoint"""
    print_section("Test 3: Status Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        print("✅ Status endpoint works!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_scrape_minimal():
    """Test scraping with minimal parameters"""
    print_section("Test 4: Minimal Scrape (Default Parameters)")
    
    try:
        print("⏳ Sending request (this may take 1-2 minutes)...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/scrape-jobs",
            json={},  # Empty body - use defaults
            timeout=300  # 5 minute timeout
        )
        
        elapsed = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time taken: {elapsed:.2f} seconds")
        
        data = response.json()
        print(f"\nResults:")
        print(f"  Success: {data.get('success')}")
        print(f"  Total Jobs: {data.get('total_jobs')}")
        print(f"  Scraped At: {data.get('scraped_at')}")
        
        if data.get('total_jobs', 0) > 0:
            print(f"\n  First job sample:")
            first_job = data['jobs'][0]
            print(f"    Title: {first_job.get('title')}")
            print(f"    Company: {first_job.get('company')}")
            print(f"    Location: {first_job.get('location')}")
            print(f"    Source: {first_job.get('source_api')}")
            print(f"    Description length: {len(first_job.get('description', ''))} chars")
        
        assert response.status_code == 200
        assert data.get('success') == True
        print("\n✅ Minimal scrape test passed!")
    except requests.Timeout:
        print(f"❌ Request timed out after 300 seconds")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_scrape_with_parameters():
    """Test scraping with custom parameters"""
    print_section("Test 5: Scrape with Custom Parameters")
    
    try:
        request_data = {
            "platform": "SimplyHired",
            "keywords": ["python developer"],
            "pages": 1,
            "location": "United States"
        }
        
        print(f"Request body: {json.dumps(request_data, indent=2)}")
        print("⏳ Sending request (this may take 1-2 minutes)...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/scrape-jobs",
            json=request_data,
            timeout=300
        )
        
        elapsed = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Time taken: {elapsed:.2f} seconds")
        
        data = response.json()
        print(f"\nResults:")
        print(f"  Success: {data.get('success')}")
        print(f"  Total Jobs: {data.get('total_jobs')}")
        print(f"  Scraped At: {data.get('scraped_at')}")
        
        if data.get('total_jobs', 0) > 0:
            print(f"\n  Sample jobs:")
            for i, job in enumerate(data['jobs'][:3], 1):
                print(f"\n  Job {i}:")
                print(f"    Title: {job.get('title')}")
                print(f"    Company: {job.get('company')}")
                print(f"    Location: {job.get('location')}")
                print(f"    Source: {job.get('source_api')}")
                print(f"    Posted: {job.get('posted_date', '')[:10]}")
        
        assert response.status_code == 200
        assert data.get('success') == True
        print("\n✅ Custom parameters test passed!")
    except requests.Timeout:
        print(f"❌ Request timed out after 300 seconds")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_invalid_parameters():
    """Test API with invalid parameters"""
    print_section("Test 6: Invalid Parameters (Error Handling)")
    
    # Test 1: Invalid keywords (not a list)
    print("\n6a. Testing invalid keywords (string instead of list)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/scrape-jobs",
            json={"keywords": "python developer"},  # Should be a list
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 400
        assert response.json().get('success') == False
        print("✅ Invalid keywords handled correctly!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Invalid pages (negative number)
    print("\n6b. Testing invalid pages (negative number)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/scrape-jobs",
            json={"pages": -1},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 400
        assert response.json().get('success') == False
        print("✅ Invalid pages handled correctly!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Empty keywords list
    print("\n6c. Testing empty keywords list...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/scrape-jobs",
            json={"keywords": []},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 400
        assert response.json().get('success') == False
        print("✅ Empty keywords handled correctly!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def run_all_tests(skip_scraping=False):
    """Run all tests"""
    print("\n" + "🧪 JOB SCRAPER API TEST SUITE ".center(60, "="))
    print(f"Testing API at: {BASE_URL}")
    print(f"Skip scraping tests: {skip_scraping}")
    
    # Basic tests (fast)
    test_root()
    test_health()
    test_status()
    
    # Scraping tests (slow)
    if not skip_scraping:
        test_scrape_minimal()
        # test_scrape_with_parameters()  # Uncomment for full test
    else:
        print_section("Skipping Scraping Tests")
        print("Run with skip_scraping=False to test actual scraping")
    
    # Error handling tests
    test_invalid_parameters()
    
    print_section("✅ ALL TESTS COMPLETED")
    print("\nNext steps:")
    print("1. Review the results above")
    print("2. If all tests passed, deploy to Render")
    print("3. Test the deployed API with the same script (change BASE_URL)")

if __name__ == "__main__":
    import sys
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ API is running!")
    except Exception as e:
        print(f"❌ Error: Cannot connect to API at {BASE_URL}")
        print(f"   Make sure the API is running: python api.py")
        sys.exit(1)
    
    # Ask user whether to skip scraping tests
    print("\n⚠️  Scraping tests can take 1-5 minutes each")
    skip = input("Skip scraping tests? (y/N): ").strip().lower()
    skip_scraping = skip == 'y'
    
    run_all_tests(skip_scraping=skip_scraping)
