# Postman Collection for Job Scraper API Testing

This guide will help you test the Job Scraper API using Postman, especially for long-running scraping operations.

## 📥 **Setup in Postman**

### **Step 1: Create a New Collection**
1. Open Postman
2. Click **"New"** → **"Collection"**
3. Name it: `Job Scraper API - Local Testing`
4. Save

### **Step 2: Set Collection Variables**
1. Click on your collection
2. Go to **"Variables"** tab
3. Add variable:
   - Variable: `base_url`
   - Initial Value: `http://localhost:8080`
   - Current Value: `http://localhost:8080`
4. Save

---

## 🔧 **API Endpoints to Add**

### **Request 1: Health Check** ✅

**Method:** `GET`  
**URL:** `{{base_url}}/health`  
**Headers:** None needed

**Expected Response (200 OK):**
```json
{
    "status": "healthy",
    "timestamp": "2025-11-13T...",
    "scraping_status": "idle",
    "browser": {
        "available": true,
        "message": "Chromium browser found",
        "path": "/ms-playwright"
    },
    "environment": {
        "playwright_path": "/ms-playwright",
        "python_version": "3.11.14",
        "platform": "Generic",
        "port": "8080"
    }
}
```

**Tests (optional - add in "Tests" tab):**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("API is healthy", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.status).to.eql("healthy");
});

pm.test("Browser is available", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.browser.available).to.be.true;
});
```

---

### **Request 2: API Info** ℹ️

**Method:** `GET`  
**URL:** `{{base_url}}/`  
**Headers:** None needed

**Expected Response (200 OK):**
```json
{
    "name": "Job Scraper API",
    "version": "1.0.0",
    "endpoints": {
        "POST /api/scrape-jobs": "Scrape jobs from job boards",
        "GET /health": "Health check",
        "GET /api/status": "Get scraping status"
    },
    "status": "running"
}
```

---

### **Request 3: Check Status** 📊

**Method:** `GET`  
**URL:** `{{base_url}}/api/status`  
**Headers:** None needed

**Expected Response (200 OK):**
```json
{
    "status": "idle",  // or "running", "completed", "error"
    "jobs_count": 0,
    "last_heartbeat": null
}
```

---

### **Request 4: Quick Scrape Test (1 page)** ⚡

**Method:** `POST`  
**URL:** `{{base_url}}/api/scrape-jobs`  
**Headers:**
- `Content-Type`: `application/json`

**Body (raw JSON):**
```json
{
    "platform": "SimplyHired",
    "keywords": ["python developer"],
    "pages": 1,
    "location": "United States"
}
```

**Expected Response (200 OK - takes 30-90 seconds):**
```json
{
    "success": true,
    "total_jobs": 15,
    "scraped_at": "2025-11-13T...",
    "jobs": [
        {
            "job_id": "abc123",
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "New York, NY",
            "job_type": "Full-time",
            "description": "...",
            "url": "https://...",
            "skills_required": "Python, Django, AWS",
            "posted_date": "2025-11-13T...",
            "salary": "$100k - $150k",
            "source_api": "SimplyHired",
            "fetched_at": "2025-11-13T..."
        }
    ]
}
```

**⚠️ Important Postman Settings for This Request:**
1. Go to Settings (⚙️) → General
2. Set **Request timeout** to: `180000` ms (3 minutes)
3. For this specific request, you may need longer

---

### **Request 5: FULL SCRAPE TEST (All Platforms, Multiple Keywords)** 🚀

**Method:** `POST`  
**URL:** `{{base_url}}/api/scrape-jobs`  
**Headers:**
- `Content-Type`: `application/json`

**Body (raw JSON):**
```json
{
    "platform": "all",
    "keywords": [
        "python developer",
        "data scientist",
        "machine learning engineer"
    ],
    "pages": 3,
    "location": "United States"
}
```

**⚠️ CRITICAL Postman Settings for Full Scrape:**

1. **Timeout Settings:**
   - File → Settings → General
   - Set **Request timeout in ms**: `3600000` (1 hour)

2. **Keep Postman Running:**
   - Don't close Postman during the request
   - Monitor the response in real-time

**Expected Duration:** 30-60 minutes  
**Expected Response:** Same format as above, but with more jobs

---

### **Request 6: Test Single Platform - SimplyHired** 🎯

**Method:** `POST`  
**URL:** `{{base_url}}/api/scrape-jobs`  
**Body (raw JSON):**
```json
{
    "platform": "SimplyHired",
    "keywords": ["python developer", "data scientist"],
    "pages": 2,
    "location": "United States"
}
```

**Expected Duration:** 10-20 minutes

---

### **Request 7: Test Single Platform - Glassdoor** 🎯

**Method:** `POST`  
**URL:** `{{base_url}}/api/scrape-jobs`  
**Body (raw JSON):**
```json
{
    "platform": "Glassdoor",
    "keywords": ["python developer"],
    "pages": 2,
    "location": "United States"
}
```

**Expected Duration:** 10-20 minutes

---

### **Request 8: Test Single Platform - Talent.com** 🎯

**Method:** `POST`  
**URL:** `{{base_url}}/api/scrape-jobs`  
**Body (raw JSON):**
```json
{
    "platform": "Talent.com",
    "keywords": ["python developer"],
    "pages": 2,
    "location": "United States"
}
```

**Expected Duration:** 10-20 minutes

---

## 📋 **Testing Strategy (Recommended Order)**

### **Phase 1: Quick Validation (5 minutes)**
1. ✅ Run **Health Check** - Verify API is up
2. ✅ Run **API Info** - Verify endpoints
3. ✅ Run **Check Status** - Verify status tracking

### **Phase 2: Quick Scrape Test (2-3 minutes)**
4. ✅ Run **Quick Scrape Test** (1 page, 1 keyword)
   - Verifies scraping works
   - Verifies browser is functional
   - Verifies data format is correct

### **Phase 3: Medium Test (15-20 minutes)**
5. ✅ Run **Single Platform Test** (SimplyHired, 2 pages, 2 keywords)
   - Verifies multi-keyword scraping
   - Verifies pagination works
   - Check logs: `docker logs -f job-scraper-api`

### **Phase 4: Full Production Test (30-60 minutes)**
6. ✅ Run **Full Scrape Test** (all platforms, 3 keywords, 3 pages)
   - Run before bed or during lunch
   - Monitor Docker logs
   - Save response to file

---

## 📊 **Monitoring During Long Tests**

### **In Postman:**
- Watch the bottom-left corner for "Sending request..."
- Don't close Postman!
- Response will appear when complete

### **In Terminal (PowerShell):**
```powershell
# Watch logs in real-time
docker logs -f job-scraper-api

# Check if container is running
docker ps

# Check resource usage
docker stats job-scraper-api
```

### **In Browser:**
While scraping is running, you can still check status:
```
http://localhost:8080/api/status
```
Should show:
```json
{
    "status": "running",
    "jobs_count": 45,  // increases over time
    "last_heartbeat": "2025-11-13T..."
}
```

---

## 🎯 **Postman Collection JSON (Import This)**

Save this as `job-scraper-api.postman_collection.json` and import it:

```json
{
    "info": {
        "name": "Job Scraper API - Local Testing",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Health Check",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/health",
                    "host": ["{{base_url}}"],
                    "path": ["health"]
                }
            }
        },
        {
            "name": "API Info",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/",
                    "host": ["{{base_url}}"],
                    "path": [""]
                }
            }
        },
        {
            "name": "Check Status",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/status",
                    "host": ["{{base_url}}"],
                    "path": ["api", "status"]
                }
            }
        },
        {
            "name": "Quick Scrape Test (1 page)",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"platform\": \"SimplyHired\",\n    \"keywords\": [\"python developer\"],\n    \"pages\": 1,\n    \"location\": \"United States\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/scrape-jobs",
                    "host": ["{{base_url}}"],
                    "path": ["api", "scrape-jobs"]
                }
            }
        },
        {
            "name": "Full Scrape Test (ALL PLATFORMS)",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"platform\": \"all\",\n    \"keywords\": [\"python developer\", \"data scientist\", \"machine learning engineer\"],\n    \"pages\": 3,\n    \"location\": \"United States\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/scrape-jobs",
                    "host": ["{{base_url}}"],
                    "path": ["api", "scrape-jobs"]
                }
            }
        }
    ],
    "variable": [
        {
            "key": "base_url",
            "value": "http://localhost:8080"
        }
    ]
}
```

---

## ✅ **Success Criteria Before DigitalOcean Deployment**

- [ ] Health check returns `"status": "healthy"`
- [ ] Browser shows `"available": true`
- [ ] Quick scrape (1 page) completes in <2 minutes
- [ ] Quick scrape returns jobs with all fields populated
- [ ] Medium scrape (2 pages, 2 keywords) completes successfully
- [ ] Full scrape completes without errors
- [ ] No memory/timeout errors in Docker logs
- [ ] API returns proper JSON format
- [ ] Status endpoint updates during scraping

---

## 🐛 **Troubleshooting**

### **Postman Times Out:**
```
Error: Request timeout
```
**Solution:**
- Increase timeout: Settings → General → Request timeout
- Set to `3600000` ms (1 hour)

### **Container Crashes During Scrape:**
```powershell
# Check logs
docker logs job-scraper-api

# Increase memory for Docker Desktop
# Docker Desktop → Settings → Resources → Memory → 4GB
```

### **No Response After 1 Hour:**
```powershell
# Check if container is still running
docker ps

# Check logs for errors
docker logs job-scraper-api

# Check status
curl http://localhost:8080/api/status
```

---

**Save this file as reference and use the Postman collection for thorough testing!** 🚀
