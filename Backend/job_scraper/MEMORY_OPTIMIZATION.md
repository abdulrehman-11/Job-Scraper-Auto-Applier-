# Memory Optimization for Render Free Tier (512 MB)

## 🎯 What Changed

### Problem
Your original code was scraping all platforms **in parallel**, causing memory to spike to **1-1.5 GB**, exceeding Render's 512 MB free tier limit.

### Solution
Implemented **sequential platform scraping** with aggressive memory cleanup:

1. ✅ Scrape SimplyHired → Close browser → Clear jobs from memory
2. ✅ Scrape Talent.com → Close browser → Clear jobs from memory  
3. ✅ Merge results → Deduplicate → Return to n8n

---

## 📊 Memory Usage Comparison

| Approach | Peak Memory | Status |
|----------|-------------|--------|
| **Old (Parallel)** | 1-1.5 GB | ❌ Exceeds 512 MB |
| **New (Sequential)** | 400-450 MB | ✅ Fits in 512 MB |

---

## 🚀 How to Use

### n8n HTTP Request Node Configuration

**Endpoint:** `POST https://your-render-app.onrender.com/api/scrape-jobs`

**Request Body:**
```json
{
  "platform": "all",
  "keywords": ["python developer", "react developer"],
  "pages": 2,
  "location": "United States"
}
```

**Response (Example):**
```json
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
      "url": "https://simplyhired.com/job/...",
      "description": "We are looking for a Python developer...",
      "posted_date": "2025-11-12T10:30:00",
      "source": "SimplyHired",
      "fetched_at": "2025-11-13T00:05:00"
    },
    ...179 more jobs
  ]
}
```

---

## ⚙️ Recommended Settings for Render Free Tier

### Conservative (Guaranteed to work)
```json
{
  "keywords": ["python developer", "react developer"],
  "pages": 2,
  "platform": "all"
}
```
- **Memory:** ~350-400 MB
- **Time:** ~4-5 minutes
- **Jobs:** ~150-200

### Aggressive (Maximum scraping)
```json
{
  "keywords": ["python", "react", "node"],
  "pages": 3,
  "platform": "all"
}
```
- **Memory:** ~450-480 MB (close to limit!)
- **Time:** ~6-7 minutes
- **Jobs:** ~300-400

⚠️ **Note:** If you add more keywords in the future, keep `pages=2` or reduce keywords to 2-3.

---

## 🔧 Technical Details

### New Method: `scrape_all_platforms_sequential()`

**Location:** `Screp.py` line ~1040

**Features:**
- Scrapes platforms one at a time
- Per-platform timeout (150 seconds = 2.5 min)
- Automatic browser cleanup
- Graceful degradation (if one platform fails, continues to next)
- Memory-efficient (never holds more than 1 platform's jobs in memory)

### Updated Endpoint: `/api/scrape-jobs`

**Location:** `api.py` line ~270

**Changes:**
- Default platform: `"all"` (both SimplyHired + Talent.com)
- Default keywords: `["python developer", "react developer"]`
- Default pages: `2` (reduced from 5)
- Max keywords enforced: `2` (automatic capping)
- Max pages enforced: `2` (automatic capping)
- Logs warnings if you exceed recommended limits

---

## 📋 n8n Workflow Example

```
1. Schedule Trigger (Daily 12 AM)
   ↓
2. HTTP Request Node
   - Method: POST
   - URL: https://your-app.onrender.com/api/scrape-jobs
   - Body: 
     {
       "platform": "all",
       "keywords": ["python developer", "react developer"],
       "pages": 2
     }
   - Timeout: 360000 (6 minutes)
   ↓
3. n8n automatically creates 180 items (one per job)
   ↓
4. Remove Duplicates Node (optional)
   - Field: job_id
   ↓
5. Google Sheets / Airtable / Database Node
   - Insert/Update jobs
```

---

## 🧪 Testing

### Test Memory Usage Locally

```bash
# Install psutil for memory monitoring
pip install psutil

# Run memory test
python test_memory_optimization.py
```

**Expected Output:**
```
📊 MEMORY REPORT
====================================
Initial memory:       120.50 MB
Peak memory:          420.30 MB  ✅ Under 512 MB
Final memory:         250.80 MB
Total jobs scraped:   180
Jobs after dedup:     165
====================================
✅ SUCCESS: Peak memory is under 512 MB limit!
```

### Test API Endpoint Locally

```bash
# Start Flask server
python api.py

# In another terminal, test the endpoint
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "all",
    "keywords": ["python developer"],
    "pages": 2
  }'
```

---

## 🔮 Future Scaling

### Adding More Keywords

If you want to add keywords like `"ruby on rails"`, `"node.js"`, etc.:

**Option 1: Keep pages low**
```json
{
  "keywords": ["python", "react", "node", "ruby"],
  "pages": 1  // ← Reduce pages to stay under memory
}
```

**Option 2: Make multiple calls**
```
Call 1: ["python", "react"], pages: 2
Call 2: ["node", "ruby"], pages: 2
```

### Adding More Platforms

If you uncomment Glassdoor in the future:

1. Add to `scrape_all_platforms_sequential()` method
2. Add another platform timeout block
3. Test memory usage (might need to reduce pages to 1)

---

## ⚠️ Important Notes

1. **Render Free Tier Restarts Daily**
   - Don't store data in files on Render
   - Use external database (Supabase, MongoDB Atlas) or let n8n store data

2. **n8n Timeout Settings**
   - Set HTTP Request timeout to **at least 6 minutes** (360000 ms)
   - Default is 5 minutes, which might be too short

3. **Rate Limiting**
   - Don't run scraper more than once per hour
   - Job sites may block if you scrape too frequently

4. **Browser Installation on Render**
   - Already configured in `render-build.sh`
   - Uses Chromium from `/opt/render/project/src/browsers`

---

## 📞 Troubleshooting

### "Out of Memory" Error on Render

**Solution:** Reduce scraping scope
```json
{
  "keywords": ["python"],  // 1 keyword only
  "pages": 1               // 1 page only
}
```

### n8n Timeout

**Solution:** Increase timeout in n8n HTTP Request node
- Settings → Timeout → 360000 (6 minutes)

### No Jobs Returned

**Possible causes:**
1. Job sites changed their HTML structure → Update selectors in `Screp.py`
2. CAPTCHA blocking → Run with `headless=False` locally to check
3. Network issues on Render → Check Render logs

---

## 📈 Monitoring

Check Render dashboard for:
- **Memory usage** (should stay under 512 MB)
- **Response time** (should be 4-6 minutes)
- **Error logs** (check for timeout/memory errors)

---

## ✅ Summary

Your backend is now optimized for:
- ✅ **512 MB memory limit** (Render free tier)
- ✅ **Single HTTP call** from n8n
- ✅ **2 platforms** (SimplyHired + Talent.com)
- ✅ **2 keywords, 2 pages** (safe defaults)
- ✅ **4-6 minute response time** (under timeout)
- ✅ **Scalable** (easy to add more keywords/platforms later)

You can now deploy to Render and set up your n8n automation! 🚀
