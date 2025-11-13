"""
Local testing script for sequential scraping
Run this to test scraping with browser visible + memory monitoring
"""
import asyncio
import traceback
from datetime import datetime
from Screp import JobScraper

async def test_local():
    """Test scraping locally with visible browser"""
    
    print("="*70)
    print("🧪 LOCAL SCRAPING TEST")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("Browser: VISIBLE (headless=False)")
    print("You can watch the scraping happen in Chrome!")
    print("="*70)
    
    # Configuration
    keywords = ['python developer']  # Start with 1 keyword for quick test
    location = 'United States'
    max_pages = 1  # Just 1 page for quick test
    
    print(f"\n📋 Test Configuration:")
    print(f"  Keywords: {keywords}")
    print(f"  Location: {location}")
    print(f"  Pages per keyword: {max_pages}")
    print(f"  Platforms: SimplyHired + Talent.com")
    
    try:
        # Create scraper with VISIBLE browser (headless=False)
        print(f"\n🚀 Initializing scraper...")
        scraper = JobScraper(headless=False)  # ← Browser will be VISIBLE
        
        # Use the new sequential method
        print(f"\n🎯 Starting sequential scraping...")
        start_time = datetime.now()
        
        jobs = await scraper.scrape_all_platforms_sequential(
            keywords=keywords,
            location=location,
            max_pages=max_pages,
            platform_timeout=180  # 3 min timeout for local testing
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Deduplication
        print(f"\n🔄 Processing results...")
        scraper.remove_duplicates()
        scraper.filter_last_24_hours()
        
        final_jobs = scraper.get_jobs()
        
        # Results
        print("\n" + "="*70)
        print("📊 TEST RESULTS")
        print("="*70)
        print(f"Total jobs scraped:     {len(jobs)}")
        print(f"Jobs after dedup:       {len(final_jobs)}")
        print(f"Duration:               {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print("="*70)
        
        # Show sample jobs
        if final_jobs:
            print(f"\n📄 Sample Jobs (first 3):")
            for i, job in enumerate(final_jobs[:3], 1):
                print(f"\n{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['location']}")
                print(f"   Source: {job['source']}")
                print(f"   Posted: {job['posted_date'][:10]}")
                print(f"   Description length: {len(job.get('description', ''))} chars")
        else:
            print("\n⚠️  No jobs found!")
            print("Possible reasons:")
            print("  1. Job sites changed their HTML structure")
            print("  2. Network/connection issues")
            print("  3. Sites detected automation")
            print("\nCheck the browser window for clues!")
        
        # Save results
        if final_jobs:
            scraper.save_to_json('test_output.json')
            print(f"\n💾 Results saved to: test_output.json")
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   {str(e)}")
        print(f"\n📋 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    print("\n⚠️  MEMORY MONITORING TIP:")
    print("   Open Task Manager → Performance → Memory")
    print("   Watch memory usage during scraping")
    print("   Press CTRL+C to stop if needed\n")
    
    input("Press ENTER to start test...")
    
    try:
        asyncio.run(test_local())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test stopped by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        traceback.print_exc()
