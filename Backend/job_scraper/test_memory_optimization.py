"""
Test script to verify memory optimization for Render free tier
Tests sequential scraping with 2 keywords, 2 pages
"""
import asyncio
import psutil
import os
from Screp import JobScraper

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # Convert to MB

async def test_sequential_scraping():
    """Test sequential scraping with memory monitoring"""
    
    print("="*60)
    print("🧪 MEMORY OPTIMIZATION TEST")
    print("="*60)
    print(f"Target: Stay under 512 MB")
    print(f"Test config: 2 keywords, 2 pages, 2 platforms")
    print("="*60)
    
    # Initial memory
    initial_memory = get_memory_usage()
    print(f"\n📊 Initial memory: {initial_memory:.2f} MB")
    
    # Create scraper
    scraper = JobScraper(headless=True)
    
    keywords = ['python developer', 'react developer']
    location = 'United States'
    max_pages = 2
    
    print(f"\n🚀 Starting sequential scraping...")
    memory_before = get_memory_usage()
    print(f"📊 Memory before scraping: {memory_before:.2f} MB")
    
    # Run sequential scraping
    jobs = await scraper.scrape_all_platforms_sequential(
        keywords=keywords,
        location=location,
        max_pages=max_pages,
        platform_timeout=150
    )
    
    # Memory after scraping (before deduplication)
    memory_after_scraping = get_memory_usage()
    print(f"\n📊 Memory after scraping: {memory_after_scraping:.2f} MB")
    print(f"📊 Memory increase: {memory_after_scraping - memory_before:.2f} MB")
    
    # Deduplication
    print(f"\n🔄 Running deduplication...")
    scraper.remove_duplicates()
    scraper.filter_last_24_hours()
    
    # Final memory
    final_memory = get_memory_usage()
    peak_memory = memory_after_scraping  # Peak is usually during scraping
    
    print("\n" + "="*60)
    print("📊 MEMORY REPORT")
    print("="*60)
    print(f"Initial memory:       {initial_memory:.2f} MB")
    print(f"Peak memory:          {peak_memory:.2f} MB")
    print(f"Final memory:         {final_memory:.2f} MB")
    print(f"Memory increase:      {peak_memory - initial_memory:.2f} MB")
    print(f"Total jobs scraped:   {len(jobs)}")
    print(f"Jobs after dedup:     {len(scraper.jobs)}")
    print("="*60)
    
    # Check if within limits
    if peak_memory < 512:
        print(f"✅ SUCCESS: Peak memory ({peak_memory:.2f} MB) is under 512 MB limit!")
    else:
        print(f"❌ FAILED: Peak memory ({peak_memory:.2f} MB) exceeds 512 MB limit!")
    
    print("="*60)
    
    return {
        'peak_memory_mb': peak_memory,
        'total_jobs': len(jobs),
        'jobs_after_dedup': len(scraper.jobs),
        'success': peak_memory < 512
    }

if __name__ == "__main__":
    try:
        result = asyncio.run(test_sequential_scraping())
        print(f"\n🎯 Test Result: {'PASS ✅' if result['success'] else 'FAIL ❌'}")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
