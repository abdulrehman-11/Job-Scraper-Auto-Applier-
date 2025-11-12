# 🔗 n8n Integration Guide - Job Scraper API

## ✅ Your Deployed API
**URL**: `https://job-scraper-api-o5mm.onrender.com/`

---

## 🎯 Best Option: HTTP Request Node

**YES**, the **HTTP Request node** is the BEST option for your use case because:

✅ **Direct API Integration** - Clean, simple REST API call  
✅ **Built-in Error Handling** - n8n handles retries, timeouts  
✅ **Easy Configuration** - No code required  
✅ **Supports Long Running Requests** - Configurable timeout  
✅ **JSON Response** - Automatically parsed  

### Alternative Options (NOT Recommended):
- ❌ **Webhook** - Overkill for this, you need to call API not receive calls
- ❌ **Code Node** - Unnecessary complexity when HTTP Request works
- ❌ **Custom Integration** - Time-consuming to build

---

## 📋 HTTP Request Node Configuration

### **Step-by-Step Setup:**

#### 1. **Add HTTP Request Node**
- Drag "HTTP Request" node to your workflow
- Connect it to your trigger (Schedule/Manual)

#### 2. **Configure the Node:**

| **Field** | **Value** | **Notes** |
|-----------|-----------|-----------|
| **Method** | `POST` | Required for scraping |
| **URL** | `https://job-scraper-api-o5mm.onrender.com/api/scrape-jobs` | Your deployed endpoint |
| **Authentication** | `None` | (Add later if needed) |
| **Send Body** | `✓ Enabled` | |
| **Body Content Type** | `JSON` | |
| **Timeout** | `600000` | 10 minutes (600,000 ms) |

#### 3. **Request Body (JSON):**

```json
{
  "platform": "SimplyHired",
  "keywords": ["python developer", "data scientist"],
  "pages": 2,
  "location": "United States"
}
```

#### 4. **Advanced Options:**

Go to **Options** → Add these:

| **Option** | **Value** | **Why** |
|------------|-----------|---------|
| **Timeout** | `600000` | Scraping takes time (10 min max) |
| **Redirect** | `Follow Redirect` | Handle any redirects |
| **Ignore SSL Issues** | `false` | Keep secure |
| **Batch Size** | `1` | One request at a time |

---

## 🔧 Complete Node Configuration (Copy-Paste Ready)

### **HTTP Request Node Settings:**

```javascript
{
  "method": "POST",
  "url": "https://job-scraper-api-o5mm.onrender.com/api/scrape-jobs",
  "authentication": "none",
  "sendBody": true,
  "bodyContentType": "json",
  "jsonBody": {
    "platform": "SimplyHired",
    "keywords": ["python developer", "data scientist"],
    "pages": 2,
    "location": "United States"
  },
  "options": {
    "timeout": 600000,
    "redirect": {
      "redirect": {
        "followRedirects": true
      }
    }
  }
}
```

---

## 📊 API Endpoints Reference

### **1. Scrape Jobs (Main Endpoint)**
```
POST https://job-scraper-api-o5mm.onrender.com/api/scrape-jobs
```

**Request Body:**
```json
{
  "platform": "SimplyHired",      // or "Glassdoor", "Talent.com", "all", null
  "keywords": ["python", "react"], // Array of job keywords
  "pages": 2,                      // Number of pages (1-5 recommended)
  "location": "United States"      // Job location
}
```

**Response:**
```json
{
  "success": true,
  "total_jobs": 45,
  "scraped_at": "2025-11-12T10:30:00.000000",
  "jobs": [
    {
      "job_id": "123abc",
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "Remote",
      "job_type": "Full-time",
      "description": "...",
      "url": "https://...",
      "skills_required": "Python, Django, AWS",
      "posted_date": "2 days ago",
      "salary": "$120k - $150k",
      "source_api": "SimplyHired",
      "fetched_at": "2025-11-12T10:30:00"
    }
  ]
}
```

### **2. Health Check**
```
GET https://job-scraper-api-o5mm.onrender.com/health
```

### **3. Scraping Status**
```
GET https://job-scraper-api-o5mm.onrender.com/api/status
```

---

## 🚀 Complete n8n Workflow Example

### **Workflow Steps:**

1. **Schedule Trigger** → Runs daily at 9 AM
2. **HTTP Request** → Calls your scraper API
3. **IF Node** → Check if success = true
4. **Split In Batches** → Process jobs in chunks
5. **Code Node** → Transform/filter jobs
6. **Database/Sheets** → Store results
7. **Notification** → Send summary

### **Visual Flow:**
```
[Schedule Trigger] → [HTTP Request] → [Check Success] → [Split Jobs] → [Process Each Job] → [Save to DB] → [Notify]
```

---

## 💡 Sample Workflow Configurations

### **Configuration 1: Simple Daily Scrape**

```json
{
  "nodes": [
    {
      "name": "Daily Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 24}]
        }
      }
    },
    {
      "name": "Scrape Jobs",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://job-scraper-api-o5mm.onrender.com/api/scrape-jobs",
        "options": {"timeout": 600000},
        "bodyParametersJson": {
          "platform": "all",
          "keywords": ["python developer"],
          "pages": 1,
          "location": "United States"
        }
      }
    }
  ]
}
```

### **Configuration 2: Multi-Platform Scrape**

Use **Loop Over Items** to scrape different platforms:

```javascript
// In Code Node - Generate Requests
return [
  { json: { platform: "SimplyHired", keywords: ["python"], pages: 2 } },
  { json: { platform: "Glassdoor", keywords: ["python"], pages: 1 } },
  { json: { platform: "Talent.com", keywords: ["python"], pages: 2 } }
];
```

---

## 🔍 Processing the Response

### **Accessing Job Data in n8n:**

After HTTP Request, the response is available at:

```javascript
// All jobs array
{{ $json.jobs }}

// Total count
{{ $json.total_jobs }}

// Individual job fields
{{ $json.jobs[0].title }}
{{ $json.jobs[0].company }}
{{ $json.jobs[0].url }}
```

### **Split Jobs into Individual Items:**

Use **Split Out** node or Code node:

```javascript
// Code Node - Split jobs into separate items
const jobs = $input.first().json.jobs;
return jobs.map(job => ({ json: job }));
```

---

## 🎛️ Recommended Workflow Structure

### **Complete Production Workflow:**

```
1. [Schedule Trigger - Daily 9 AM]
   ↓
2. [HTTP Request - Call Scraper API]
   ↓
3. [IF - Check Success]
   ├─ True ↓
   │   [Code - Split Jobs]
   │   ↓
   │   [Filter - Only Full-time]
   │   ↓
   │   [Deduplicate - Remove Existing]
   │   ↓
   │   [Airtable/Notion - Save Jobs]
   │   ↓
   │   [Slack - Send Summary]
   │
   └─ False ↓
       [Slack - Send Error Alert]
```

---

## ⚙️ Advanced Configuration Tips

### **1. Handle Long Scraping Times**

```javascript
// Set higher timeout for large scrapes
{
  "timeout": 900000  // 15 minutes for large requests
}
```

### **2. Error Handling**

Add **Error Trigger** node:
```javascript
{
  "conditions": {
    "boolean": [
      {"value1": "={{ $json.success }}", "value2": false}
    ]
  }
}
```

### **3. Rate Limiting**

Add **Wait** node between requests:
```javascript
{
  "amount": 30,
  "unit": "seconds"
}
```

### **4. Dynamic Parameters**

Use expressions for dynamic values:
```javascript
{
  "keywords": "={{ $json.search_terms }}",
  "location": "={{ $json.user_location }}",
  "pages": "={{ $json.pages_to_scrape }}"
}
```

---

## 🧪 Testing Your Integration

### **1. Test Health Endpoint First:**

```
GET https://job-scraper-api-o5mm.onrender.com/health
```

Expected: `{"status": "healthy", ...}`

### **2. Test Small Scrape:**

```json
{
  "platform": "SimplyHired",
  "keywords": ["python"],
  "pages": 1,
  "location": "United States"
}
```

### **3. Test in n8n:**

- Click "Execute Node" on HTTP Request
- Check output panel for job data
- Verify `success: true` and jobs array

---

## ⚠️ Important Considerations

### **Timeout Settings:**
- **Free Tier Render**: 30-second HTTP timeout
- **Your API**: 10-minute internal timeout
- **n8n HTTP Request**: Set to 600000ms (10 min)
- **Issue**: Render may timeout before scraping completes

### **Solutions:**

1. **Reduce Scraping Scope:**
   ```json
   {
     "pages": 1,  // Keep it small
     "keywords": ["python"]  // Single keyword
   }
   ```

2. **Use Webhook Pattern** (Advanced):
   - API starts scraping → returns immediately
   - Sends results to n8n webhook when done
   - Better for long-running scrapes

3. **Upgrade Render Plan**:
   - Paid plans have longer timeouts
   - Better for production use

---

## 📱 Sample Platforms Configuration

### **SimplyHired (Recommended - Fastest)**
```json
{"platform": "SimplyHired", "keywords": ["python"], "pages": 2}
```

### **Talent.com (Good)**
```json
{"platform": "Talent.com", "keywords": ["javascript"], "pages": 2}
```

### **Glassdoor (Slower - May have CAPTCHA)**
```json
{"platform": "Glassdoor", "keywords": ["data scientist"], "pages": 1}
```

### **All Platforms (Longest)**
```json
{"platform": "all", "keywords": ["developer"], "pages": 1}
```

---

## 🔐 Security Best Practices

### **1. Add API Key Authentication (Future)**

Update your `api.py` to require API key, then in n8n:

```javascript
{
  "authentication": "headerAuth",
  "headerAuth": {
    "name": "X-API-Key",
    "value": "your-secret-key"
  }
}
```

### **2. Environment Variables in n8n**

Store sensitive data in n8n credentials:
- API URL
- API keys
- Database credentials

---

## 📊 Expected Performance

| **Configuration** | **Time** | **Jobs** | **Recommended** |
|-------------------|----------|----------|-----------------|
| 1 platform, 1 page | 1-2 min | ~20 jobs | ✅ Best for testing |
| 1 platform, 2 pages | 2-4 min | ~40 jobs | ✅ Good for production |
| All platforms, 1 page | 3-5 min | ~50 jobs | ⚠️ May timeout on free tier |
| All platforms, 2 pages | 6-10 min | ~100 jobs | ❌ Likely timeout |

---

## 🎯 Quick Start Checklist

- [ ] Test health endpoint
- [ ] Create HTTP Request node in n8n
- [ ] Configure POST to `/api/scrape-jobs`
- [ ] Set timeout to 600000ms
- [ ] Add JSON body with parameters
- [ ] Test with 1 page, 1 keyword
- [ ] Add Split Out node for jobs
- [ ] Connect to your storage (Airtable/Notion/DB)
- [ ] Test full workflow
- [ ] Schedule trigger

---

## 🆘 Troubleshooting

### **❌ Timeout Error**
- Reduce `pages` to 1
- Use single platform
- Check Render logs

### **❌ No Jobs Returned**
- Check keywords spelling
- Verify location format
- Test different platform

### **❌ Connection Error**
- Verify API URL is correct
- Check Render service is running
- Test health endpoint

### **❌ Invalid Response**
- Check request body format
- Ensure JSON is valid
- Review API logs

---

## 📞 Support & Resources

- **API URL**: https://job-scraper-api-o5mm.onrender.com/
- **Health Check**: https://job-scraper-api-o5mm.onrender.com/health
- **n8n Docs**: https://docs.n8n.io/
- **Render Logs**: Check Render dashboard for errors

---

**Ready to integrate? Copy the HTTP Request configuration above and paste it into your n8n workflow!** 🚀
