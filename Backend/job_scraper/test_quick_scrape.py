import requests
import json

print("🧪 Testing Job Scraper API - Quick Scrape Test\n")

url = "https://job-scraper-api-o5mm.onrender.com/api/scrape-jobs"
payload = {
    "platform": "SimplyHired",
    "keywords": ["python"],
    "pages": 1,
    "location": "United States"
}

print("📡 Sending scrape request...")
print(f"   Platform: {payload['platform']}")
print(f"   Keywords: {payload['keywords']}")
print(f"   Pages: {payload['pages']}")
print("\n⏳ Waiting for response (may take 1-2 minutes)...\n")

try:
    response = requests.post(url, json=payload, timeout=120)
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ SCRAPING SUCCESSFUL!")
        print(f"   Success: {data.get('success')}")
        print(f"   Total Jobs: {data.get('total_jobs')}")
        print(f"   Scraped At: {data.get('scraped_at')}")
        
        if data.get('jobs') and len(data['jobs']) > 0:
            print(f"\n📄 Sample Jobs (First 3):")
            for i, job in enumerate(data['jobs'][:3], 1):
                print(f"\n   Job #{i}:")
                print(f"   - Title: {job.get('title')}")
                print(f"   - Company: {job.get('company')}")
                print(f"   - Location: {job.get('location')}")
                print(f"   - Type: {job.get('job_type')}")
                print(f"   - URL: {job.get('url')[:60]}...")
        else:
            print("\n⚠️  No jobs found")
    else:
        print(f"❌ Error: Status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out (Render free tier limitation)")
except Exception as e:
    print(f"❌ Error: {str(e)}")
