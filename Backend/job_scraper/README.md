# 🚀 Job Scraper REST API - Complete Setup Guide

## 📋 Overview

Your job scraping backend has been transformed into a production-ready REST API that can be:
- Called by n8n automation workflows
- Deployed on Render.com
- Accessed via HTTP requests
- Integrated into any application

---

## 🗂️ Project Structure

```
job_scraper/
├── 🎯 Core Files
│   ├── api.py                    # Flask REST API (NEW)
│   ├── Screp.py                  # Job scraper engine
│   └── config.py                 # Configuration
│
├── ⚙️ Configuration
│   ├── requirement.txt           # Dependencies (UPDATED)
│   ├── render.yaml              # Render deployment config (NEW)
│   ├── Procfile                 # Process file (NEW)
│   ├── runtime.txt              # Python version (NEW)
│   ├── .env.example             # Environment template (NEW)
│   └── .gitignore               # Git ignore rules (NEW)
│
├── 📚 Documentation
│   ├── README_API.md            # Complete API docs (NEW)
│   ├── QUICKSTART.md            # 5-min quick start (NEW)
│   ├── DEPLOYMENT.md            # Deployment guide (NEW)
│   └── PACKAGE_SUMMARY.md       # Package overview (NEW)
│
├── 🧪 Testing & Examples
│   ├── test_api.py              # API test suite (NEW)
│   └── n8n_workflow_example.json # n8n workflow (NEW)
│
└── 📝 Existing Files
    ├── jobs_output.json         # Output file
    ├── n8n_format_example.json  # Format reference
    └── *.md                     # Existing docs
```

---

## 🎯 What Was Built

### 1. REST API (`api.py`)
A Flask-based API with these endpoints:

**Main Endpoint:**
```
POST /api/scrape-jobs
```
- Accepts optional parameters (platform, keywords, pages, location)
- Scrapes jobs synchronously (waits for completion)
- Returns jobs in n8n-compatible JSON format
- Includes heartbeat logging to prevent timeouts

**Supporting Endpoints:**
```
GET /health       # Health check for monitoring
GET /api/status   # Current scraping status
GET /             # API information
```

### 2. Deployment Configuration
- **render.yaml**: One-click deployment to Render
- **Procfile**: Gunicorn with proper timeout settings
- **runtime.txt**: Python 3.11 specification
- **.env.example**: Environment variables template

### 3. Complete Documentation
- **README_API.md**: Full API documentation
- **QUICKSTART.md**: Get started in 5 minutes
- **DEPLOYMENT.md**: Step-by-step deployment guide
- **PACKAGE_SUMMARY.md**: Complete package overview

### 4. Testing Tools
- **test_api.py**: Automated test suite
- **n8n_workflow_example.json**: Import-ready n8n workflow

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Install Dependencies
```powershell
cd Backend\job_scraper
pip install -r requirement.txt
playwright install chromium
```

### Step 2: Run the API
```powershell
python api.py
```

### Step 3: Test It
```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET

# Scrape jobs
$body = @{
    platform = "SimplyHired"
    keywords = @("python developer")
    pages = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/scrape-jobs" -Method POST -Body $body -ContentType "application/json"
```

---

## 🚀 Deploy to Render (3 Minutes)

### Option 1: Automatic (Recommended)
1. Push to GitHub:
   ```bash
   git add .
   git commit -m "Add Job Scraper API"
   git push origin main
   ```

2. Go to [Render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your repo
5. Render auto-detects `render.yaml`
6. Click "Create Web Service"
7. Wait 2-3 minutes for build

### Option 2: Manual
Follow detailed steps in `DEPLOYMENT.md`

---

## 🔗 n8n Integration

### Setup HTTP Request Node
1. **Method**: POST
2. **URL**: `https://your-app.onrender.com/api/scrape-jobs`
3. **Body** (JSON):
```json
{
  "platform": "SimplyHired",
  "keywords": ["python developer"],
  "pages": 1,
  "location": "United States"
}
```
4. **Options → Timeout**: 600000 (10 minutes)

### Import Example Workflow
1. Open n8n
2. Click "Import from File"
3. Select `n8n_workflow_example.json`
4. Update the URL with your Render URL
5. Execute!

---

## 📖 Documentation Guide

**Choose your path:**

### 🏃 I want to get started FAST
→ Read **`QUICKSTART.md`** (5 minutes)

### 📚 I want complete documentation
→ Read **`README_API.md`** (15 minutes)

### 🚀 I'm ready to deploy
→ Follow **`DEPLOYMENT.md`** (10 minutes)

### 🤔 I want to understand everything
→ Read **`PACKAGE_SUMMARY.md`** (20 minutes)

---

## 🔧 API Usage Examples

### Example 1: Default Parameters
```bash
POST /api/scrape-jobs
Body: {}
```
Result: Uses default settings (python developer, 1 page, SimplyHired)

### Example 2: Custom Keywords
```bash
POST /api/scrape-jobs
Body: {
  "keywords": ["data scientist", "machine learning engineer"],
  "pages": 2
}
```
Result: Scrapes 2 pages for each keyword

### Example 3: Specific Platform
```bash
POST /api/scrape-jobs
Body: {
  "platform": "Talent.com",
  "keywords": ["software engineer"],
  "location": "Remote"
}
```
Result: Only scrapes Talent.com for remote jobs

---

## 📊 API Response Format

```json
{
  "success": true,
  "total_jobs": 20,
  "scraped_at": "2025-11-04T22:30:00.000000",
  "jobs": [
    {
      "job_id": "simplyhired_abc123",
      "title": "Python Developer",
      "company": "Tech Corp",
      "location": "Remote",
      "job_type": "Full-time",
      "description": "Full job description...",
      "url": "https://...",
      "skills_required": "Python, Django, Docker",
      "posted_date": "2025-11-04T10:30:00",
      "salary": "$120,000 - $150,000",
      "source_api": "SimplyHired",
      "fetched_at": "2025-11-04T22:30:00"
    }
  ]
}
```

---

## 🎯 Key Features

✅ **Synchronous Processing** - Waits for scraping to complete
✅ **Multi-platform** - SimplyHired, Talent.com, Glassdoor
✅ **Full Descriptions** - Extracts complete job details
✅ **Duplicate Detection** - Smart deduplication
✅ **24-hour Filter** - Only recent jobs
✅ **n8n Compatible** - Perfect for automation
✅ **Keep-alive** - Prevents timeouts with heartbeat logs
✅ **Production Ready** - Configured for Render deployment
✅ **Error Handling** - Proper HTTP status codes
✅ **CORS Enabled** - Can be called from anywhere

---

## 🧪 Testing

### Run Test Suite
```bash
python test_api.py
```

Tests include:
- Health check
- Status endpoint
- Scraping with default parameters
- Scraping with custom parameters
- Error handling (invalid parameters)

### Manual Testing

**Using curl (Git Bash/Linux/Mac):**
```bash
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{"platform": "SimplyHired", "keywords": ["python developer"], "pages": 1}'
```

**Using PowerShell (Windows):**
```powershell
$body = @{platform="SimplyHired"; keywords=@("python developer"); pages=1} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/scrape-jobs" -Method POST -Body $body -ContentType "application/json"
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:5000/api/scrape-jobs",
    json={"platform": "SimplyHired", "keywords": ["python developer"], "pages": 1},
    timeout=300
)

print(f"Jobs found: {response.json()['total_jobs']}")
```

---

## 🐛 Troubleshooting

### Issue: Import errors when running `api.py`
**Solution**: Install dependencies
```bash
pip install -r requirement.txt
```

### Issue: Playwright not found
**Solution**: Install Playwright browsers
```bash
playwright install chromium
```

### Issue: Request timeout
**Solutions**:
- Increase client timeout to 600000ms (10 minutes)
- Reduce `pages` parameter to 1
- Reduce `keywords` to 1-2
- Use single platform instead of "all"

### Issue: Empty results
**Solutions**:
- Check `api.log` and `scraper.log` for errors
- Try different keywords
- Try different platform
- Ensure internet connection is stable

### Issue: Render deployment fails
**Solutions**:
- Check build logs in Render dashboard
- Verify all required files are committed
- Ensure `render.yaml` is in root directory
- Check Python version in `runtime.txt`

---

## 📈 Performance Tips

### For Faster Results:
- Use 1 page
- Use 1-2 keywords
- Use single platform (not "all")

### For More Jobs:
- Use 3-5 pages
- Use multiple keywords
- Use "all" platforms (slower but more results)

### Optimal Settings:
```json
{
  "platform": "SimplyHired",
  "keywords": ["python developer"],
  "pages": 2
}
```
Result: ~20-40 jobs in 2-3 minutes

---

## 🔒 Security & Best Practices

### Before Production:
- [ ] Review CORS settings (restrict origins if needed)
- [ ] Consider adding API key authentication
- [ ] Set up rate limiting
- [ ] Enable HTTPS (automatic on Render)
- [ ] Review scraped sites' Terms of Service
- [ ] Comply with robots.txt

### Monitoring:
- [ ] Check Render logs regularly
- [ ] Monitor response times
- [ ] Track success/error rates
- [ ] Set up alerts for downtime

---

## 📦 What's Included vs Original

### ✅ New Files (API Package)
- `api.py` - REST API
- `render.yaml` - Deployment config
- `Procfile` - Process file
- `runtime.txt` - Python version
- `.env.example` - Environment template
- `.gitignore` - Git ignore
- `README_API.md` - API docs
- `QUICKSTART.md` - Quick start
- `DEPLOYMENT.md` - Deployment guide
- `PACKAGE_SUMMARY.md` - Overview
- `test_api.py` - Test suite
- `n8n_workflow_example.json` - Example workflow

### 🔄 Updated Files
- `requirement.txt` - Added Flask, CORS, Gunicorn

### 📝 Unchanged Files (Still Work)
- `Screp.py` - Core scraper (still works standalone)
- `config.py` - Configuration
- `jobs_output.json` - Output file
- Other test files and docs

---

## 🎓 Next Steps

### 1. Local Testing ✅
```bash
cd Backend/job_scraper
pip install -r requirement.txt
playwright install chromium
python api.py
python test_api.py
```

### 2. Deployment 🚀
```bash
git add .
git commit -m "Add Job Scraper API"
git push origin main
```
Then deploy to Render following `DEPLOYMENT.md`

### 3. n8n Integration 🔗
Import `n8n_workflow_example.json` into n8n
Update URL with your Render URL
Execute and watch the magic happen!

### 4. Customize 🎨
- Modify `config.py` for default settings
- Add more platforms to `Screp.py`
- Customize response format in `api.py`
- Add authentication/rate limiting

---

## 💡 Common Use Cases

### Use Case 1: Daily Job Alerts
```
n8n Schedule (9 AM daily)
  → API: Scrape jobs
  → Filter: Full-time only
  → Send: Email/Slack notification
```

### Use Case 2: Job Database
```
n8n Schedule (Every 4 hours)
  → API: Scrape jobs
  → Process: Extract skills
  → Store: Airtable/Google Sheets
```

### Use Case 3: Resume Matching
```
n8n Manual Trigger
  → API: Scrape jobs
  → AI: Match with resume
  → Rank: Top matches
  → Send: Report via email
```

---

## 🆘 Getting Help

### Documentation
- Start with `QUICKSTART.md`
- Check `README_API.md` for details
- Follow `DEPLOYMENT.md` for deployment
- Review `PACKAGE_SUMMARY.md` for overview

### Logs
- Check `api.log` for API logs
- Check `scraper.log` for scraping logs
- Check Render logs for deployment issues

### Testing
- Run `python test_api.py` to diagnose issues
- Test locally before deploying
- Use curl/Postman to test endpoints

### Support
- Review troubleshooting sections in docs
- Check GitHub issues
- Open new issue with error logs

---

## ✅ Verification Checklist

Before deployment:
- [ ] API runs locally without errors
- [ ] All tests pass (`python test_api.py`)
- [ ] Health check returns 200 OK
- [ ] Scraping returns jobs with descriptions
- [ ] Response format matches n8n expectations
- [ ] All files committed to Git

After deployment:
- [ ] Health check works on Render URL
- [ ] API scrapes jobs successfully
- [ ] Response time < 5 minutes for 1 page
- [ ] n8n can call API successfully
- [ ] Logs show expected output

---

## 🎉 You're All Set!

Your job scraper is now a production-ready API that:
✅ Can be called from n8n
✅ Runs on Render.com
✅ Returns complete job data
✅ Handles errors gracefully
✅ Stays alive during long scrapes
✅ Is fully documented

**Start here**: `QUICKSTART.md`

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-05  
**Status**: ✅ Production Ready  
**Maintained by**: Your Team
