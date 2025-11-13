# 🧪 Local Testing Guide

## 3 Ways to Test Memory Optimization Locally

---

## ✅ **Method 1: Direct Scraping Test** (Recommended for debugging)

**Best for:** Seeing exactly what's happening in the browser

### Run:
```bash
cd Backend/job_scraper
python test_local_scraping.py
```

### What happens:
- ✅ Browser window opens (VISIBLE)
- ✅ You can watch it scrape in real-time
- ✅ Shows detailed logs
- ✅ Saves results to `test_output.json`
- ✅ Shows memory usage summary

### Monitor Memory:
1. Open **Task Manager** (Ctrl+Shift+Esc)
2. Go to **Performance** → **Memory**
3. Watch memory usage while script runs
4. Look for "python.exe" process in **Processes** tab

### Expected Output:
```
🧪 LOCAL SCRAPING TEST
======================================================================
Started at: 18:30:45
Browser: VISIBLE (headless=False)
You can watch the scraping happen in Chrome!
======================================================================

📋 Test Configuration:
  Keywords: ['python developer']
  Location: United States
  Pages per keyword: 1
  Platforms: SimplyHired + Talent.com

🚀 Initializing scraper...
🎯 Starting sequential scraping...

============================================================
🚀 SEQUENTIAL PLATFORM SCRAPING (MEMORY OPTIMIZED)
============================================================
📍 Keywords: ['python developer']
📍 Location: United States
📍 Pages per keyword: 1
⏱️  Timeout per platform: 180s
============================================================

🎯 PHASE 1/2: SimplyHired
...
✅ SimplyHired completed: 50 jobs scraped

🎯 PHASE 2/2: Talent.com
...
✅ Talent.com completed: 40 jobs scraped

📊 SEQUENTIAL SCRAPING COMPLETED
============================================================
Total jobs collected: 90
Platforms: SimplyHired (50 jobs), Talent.com (40 jobs)
============================================================

📊 TEST RESULTS
======================================================================
Total jobs scraped:     90
Jobs after dedup:       85
Duration:               180.5 seconds (3.0 minutes)
======================================================================

📄 Sample Jobs (first 3):
1. Senior Python Developer
   Company: TechCorp
   Location: Remote
   Source: SimplyHired
   Posted: 2025-11-13
   Description length: 1250 chars
...

💾 Results saved to: test_output.json
✅ Test completed!
```

---

## ✅ **Method 2: Test via API (with visible browser)**

**Best for:** Testing the actual API endpoint you'll use in n8n

### Step 1: Set DEBUG mode
```bash
# Windows PowerShell
$env:DEBUG="true"

# Windows CMD
set DEBUG=true

# Linux/Mac
export DEBUG=true
```

### Step 2: Start API server
```bash
cd Backend/job_scraper
python api.py
```

You'll see:
```
🔍 Checking browser installation...
✅ Chromium browser ready
🚀 Starting Flask server on port 5000
📍 API endpoint: http://localhost:5000/api/scrape-jobs
🐛 DEBUG mode: Browser will be VISIBLE
```

### Step 3: Test with curl (in another terminal)
```bash
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{"platform":"all","keywords":["python developer"],"pages":1}'
```

### Monitor Memory:
Same as Method 1 - watch Task Manager

### Expected Response:
```json
{
  "success": true,
  "total_jobs": 85,
  "scraped_at": "2025-11-13T18:35:00.000000",
  "jobs": [
    {
      "job_id": "abc123",
      "title": "Senior Python Developer",
      "company": "TechCorp",
      "location": "Remote, USA",
      "url": "https://www.simplyhired.com/job/...",
      "description": "We are seeking a talented Python developer...",
      "posted_date": "2025-11-13T10:00:00",
      "source": "SimplyHired",
      "fetched_at": "2025-11-13T18:35:00"
    },
    ...84 more jobs
  ]
}
```

---

## ✅ **Method 3: Memory Optimization Test**

**Best for:** Verifying you stay under 512 MB limit

### Prerequisites:
```bash
pip install psutil
```

### Run:
```bash
cd Backend/job_scraper
python test_memory_optimization.py
```

### What it does:
- ✅ Runs headless scraping
- ✅ Monitors memory usage with `psutil`
- ✅ Reports peak memory
- ✅ Verifies < 512 MB limit

### Expected Output:
```
🧪 MEMORY OPTIMIZATION TEST
============================================================
Target: Stay under 512 MB
Test config: 2 keywords, 2 pages, 2 platforms
============================================================

📊 Initial memory: 120.50 MB
🚀 Starting sequential scraping...
📊 Memory before scraping: 125.30 MB

...scraping happens...

📊 Memory after scraping: 425.80 MB
📊 Memory increase: 300.50 MB

🔄 Running deduplication...

============================================================
📊 MEMORY REPORT
============================================================
Initial memory:       120.50 MB
Peak memory:          425.80 MB
Final memory:         250.30 MB
Memory increase:      305.30 MB
Total jobs scraped:   180
Jobs after dedup:     165
============================================================
✅ SUCCESS: Peak memory (425.80 MB) is under 512 MB limit!
============================================================

🎯 Test Result: PASS ✅
```

---

## 🐛 **Troubleshooting**

### Problem: Empty results `{"total_jobs": 0}`

**Possible causes:**

#### 1. Browser not installed
```bash
# Check if Playwright browsers are installed
playwright install chromium
```

#### 2. Headless mode detection
Sites might block headless browsers. Solution:
```bash
# Run with visible browser (Method 1 or 2 with DEBUG=true)
python test_local_scraping.py
```

#### 3. Site structure changed
Watch the browser window to see what's happening:
- Does it load the page?
- Are there errors?
- Is there a CAPTCHA?

#### 4. Network issues
```bash
# Test basic connectivity
curl https://www.simplyhired.com
```

---

### Problem: High memory usage (>512 MB)

**Solutions:**

1. **Reduce scope:**
   ```json
   {
     "keywords": ["python"],  // 1 keyword only
     "pages": 1               // 1 page only
   }
   ```

2. **Test one platform at a time:**
   ```json
   {"platform": "simplyhired", "keywords": ["python"], "pages": 1}
   ```

3. **Check for memory leaks:**
   Run test multiple times and compare peak memory

---

### Problem: Script hangs/times out

**Causes:**
- Site is slow
- Selector not found (site changed HTML)
- Network timeout

**Solutions:**

1. **Increase timeout:**
   Edit `test_local_scraping.py`:
   ```python
   platform_timeout=300  # 5 minutes instead of 3
   ```

2. **Run with visible browser** to see where it gets stuck

3. **Check logs** in console for errors

---

## 📊 **What Memory Usage to Expect**

| Configuration | Expected Peak Memory | Status |
|--------------|---------------------|---------|
| 1 keyword, 1 page, 1 platform | ~200 MB | ✅ Very safe |
| 1 keyword, 1 page, 2 platforms | ~250-300 MB | ✅ Safe |
| 2 keywords, 2 pages, 2 platforms | ~400-450 MB | ✅ Safe |
| 3 keywords, 2 pages, 2 platforms | ~480-500 MB | ⚠️ Close to limit |
| 3 keywords, 3 pages, 2 platforms | ~550-600 MB | ❌ Exceeds limit |

---

## 💡 **Quick Test Commands**

### Fastest test (1 keyword, 1 page):
```bash
python test_local_scraping.py
# Edit the file first: keywords = ['python'], max_pages = 1
```

### Test API with minimal load:
```bash
# Terminal 1
DEBUG=true python api.py

# Terminal 2
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{"keywords":["python"],"pages":1,"platform":"simplyhired"}'
```

### Full production test (2 platforms):
```bash
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{"platform":"all","keywords":["python developer","react developer"],"pages":2}'
```

---

## 📝 **Monitoring Checklist**

During your test, verify:

- [ ] Browser opens (if DEBUG=true)
- [ ] Pages load successfully
- [ ] Job cards are detected
- [ ] Descriptions are extracted
- [ ] Browser closes after each platform
- [ ] Memory stays under 512 MB (check Task Manager)
- [ ] Response time is under 6 minutes
- [ ] Jobs are returned in response
- [ ] No errors in console

---

## ✅ **Ready for Production**

If all tests pass:
1. ✅ Memory stays under 450 MB
2. ✅ Jobs are successfully scraped
3. ✅ Response time is 4-6 minutes
4. ✅ No errors in logs

Then you're ready to:
1. Push to GitHub
2. Deploy to Render
3. Set up n8n automation

---

## 🆘 **Still Having Issues?**

Check these files for errors:
- `scraper.log` - Scraping logs
- `api.log` - API logs
- Console output - Real-time errors

Common fixes:
- Update Playwright: `pip install --upgrade playwright`
- Reinstall browsers: `playwright install --force chromium`
- Clear cache: Delete `__pycache__` folders
- Check Python version: Should be 3.9+
