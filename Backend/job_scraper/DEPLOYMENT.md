# 🚀 Deployment Checklist for Job Scraper API

## Pre-Deployment Checklist

### ✅ Local Testing

- [ ] Install all dependencies
  ```bash
  pip install -r requirement.txt
  playwright install chromium
  ```

- [ ] Test API locally
  ```bash
  python api.py
  ```

- [ ] Run test suite
  ```bash
  python test_api.py
  ```

- [ ] Verify all endpoints work:
  - [ ] GET `/` - API info
  - [ ] GET `/health` - Health check
  - [ ] GET `/api/status` - Status
  - [ ] POST `/api/scrape-jobs` - Main endpoint

- [ ] Test with different parameters:
  - [ ] Default parameters (empty body)
  - [ ] Custom keywords
  - [ ] Different platforms
  - [ ] Error handling

### ✅ Code Preparation

- [ ] Update `requirement.txt` with all dependencies
- [ ] Set `headless=True` in production mode
- [ ] Remove debug prints or set `DEBUG=False`
- [ ] Review timeout settings (600s for Gunicorn)
- [ ] Check heartbeat interval (300s = 5 minutes)

### ✅ Files to Commit

Required files:
- [ ] `api.py` - Main Flask application
- [ ] `Screp.py` - Job scraper
- [ ] `config.py` - Configuration
- [ ] `requirement.txt` - Python dependencies
- [ ] `render.yaml` - Render configuration
- [ ] `Procfile` - Process file
- [ ] `.env.example` - Environment variables template
- [ ] `README_API.md` - API documentation

Optional:
- [ ] `test_api.py` - Test script
- [ ] `DEPLOYMENT.md` - This file

Do NOT commit:
- [ ] `.env` - Keep this local
- [ ] `*.log` - Log files
- [ ] `jobs_output.json` - Output file
- [ ] `__pycache__/` - Python cache

---

## Render Deployment Steps

### Method 1: Automatic (with render.yaml)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Job Scraper API"
   git push origin main
   ```

2. **Create Web Service on Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select repository: `Job-Scraper-Auto-Applier-`
   - Render detects `render.yaml` automatically
   - Click "Create Web Service"

3. **Wait for Build**
   - Watch build logs
   - Should see:
     - Installing Python dependencies
     - Installing Playwright with Chromium
     - Starting Gunicorn server

4. **Verify Deployment**
   - Check health: `https://your-app.onrender.com/health`
   - Should return `{"status": "healthy", ...}`

### Method 2: Manual Configuration

1. **Create New Web Service**
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect repository

2. **Configure Settings**
   
   **Basic Settings:**
   - Name: `job-scraper-api`
   - Region: Choose closest to you
   - Branch: `main`
   - Root Directory: `Backend/job_scraper` (if not at root)

   **Build & Deploy:**
   - Runtime: `Python 3`
   - Build Command:
     ```bash
     pip install -r requirement.txt && playwright install --with-deps chromium
     ```
   - Start Command:
     ```bash
     gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 600 --keep-alive 5 --log-level info api:app
     ```

   **Environment Variables:**
   ```
   PYTHON_VERSION=3.11.0
   DEBUG=False
   HEADLESS_MODE=True
   MAX_PAGES_PER_KEYWORD=3
   ```

   **Health Check:**
   - Path: `/health`

3. **Select Plan**
   - Free: Good for testing (may spin down)
   - Starter ($7/mo): Recommended for production

4. **Deploy**
   - Click "Create Web Service"
   - Monitor build logs

---

## Post-Deployment Verification

### ✅ Basic Checks

- [ ] Service is running (check Render dashboard)
- [ ] Health check passes
  ```bash
  curl https://your-app.onrender.com/health
  ```
- [ ] Root endpoint works
  ```bash
  curl https://your-app.onrender.com/
  ```

### ✅ API Testing

Test with curl (Linux/Mac/Git Bash):
```bash
curl -X POST https://your-app.onrender.com/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{"platform": "SimplyHired", "keywords": ["python developer"], "pages": 1}'
```

Test with PowerShell (Windows):
```powershell
$body = @{
    platform = "SimplyHired"
    keywords = @("python developer")
    pages = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://your-app.onrender.com/api/scrape-jobs" -Method POST -Body $body -ContentType "application/json"
```

Test with Python:
```python
import requests

response = requests.post(
    "https://your-app.onrender.com/api/scrape-jobs",
    json={
        "platform": "SimplyHired",
        "keywords": ["python developer"],
        "pages": 1
    },
    timeout=300
)

print(f"Status: {response.status_code}")
print(f"Jobs found: {response.json()['total_jobs']}")
```

### ✅ Performance Checks

- [ ] Response time < 5 minutes for 1 page
- [ ] Heartbeat logs appear every 5 minutes
- [ ] No timeout errors
- [ ] Jobs data is complete (has descriptions)

### ✅ Monitoring

Check Render logs for:
- [ ] `🚀 Starting scraper` - Scraping started
- [ ] `🔄 Still scraping...` - Heartbeat (every 5 min)
- [ ] `✅ Scraping completed` - Success
- [ ] `❌ Error` - Check for errors

---

## n8n Integration Setup

### ✅ Configure HTTP Request Node

1. **Add HTTP Request Node**
   - Method: `POST`
   - URL: `https://your-app.onrender.com/api/scrape-jobs`

2. **Set Headers**
   ```json
   {
     "Content-Type": "application/json"
   }
   ```

3. **Set Body**
   ```json
   {
     "platform": "SimplyHired",
     "keywords": ["python developer", "data scientist"],
     "pages": 1,
     "location": "United States"
   }
   ```

4. **Set Timeout**
   - Options → Timeout: `600000` (10 minutes)

5. **Test Execution**
   - Click "Execute Node"
   - Wait for response (1-5 minutes)
   - Verify `jobs` array in output

### ✅ Process Results in n8n

Example workflow:
```
Schedule Trigger (Daily 9 AM)
    ↓
HTTP Request (POST /api/scrape-jobs)
    ↓
Set Node (Extract jobs array)
    ↓
Split In Batches (Process each job)
    ↓
Filter (job_type = "Full-time")
    ↓
Airtable/Sheets (Store jobs)
    ↓
Slack (Notify team)
```

---

## Troubleshooting

### Issue: Build Fails on Render

**Solution:**
- Check `requirement.txt` is correct
- Verify Playwright install command includes `--with-deps chromium`
- Check Python version (use 3.9-3.11)
- Review build logs for specific errors

### Issue: API Timeout

**Symptoms:** Request times out after 30-60 seconds

**Solutions:**
- ✅ Increase n8n timeout to 600000ms
- ✅ Reduce pages to 1-2
- ✅ Reduce keywords to 1-2
- ✅ Use single platform instead of "all"
- ✅ Check Gunicorn timeout is 600s

### Issue: Empty Results

**Solutions:**
- Check logs for scraping errors
- Verify keywords are valid
- Try different platform
- Check if site structure changed

### Issue: Playwright Installation Fails

**Error:** `Playwright not installed`

**Solutions:**
- Verify build command: `playwright install --with-deps chromium`
- Check disk space (Playwright needs ~200MB)
- Try adding system dependencies to build command

### Issue: Free Tier Spins Down

**Symptom:** First request after inactivity takes 30+ seconds

**Solutions:**
- Upgrade to Starter plan ($7/mo)
- Use Render's "Always On" feature
- Setup external ping service (every 14 minutes)
- Add cron job to keep service warm

### Issue: Memory Issues

**Symptom:** Service crashes during scraping

**Solutions:**
- Reduce pages and keywords
- Use 1 worker instead of 2+
- Upgrade Render plan
- Clear browser context between keywords

---

## Maintenance

### Regular Tasks

**Weekly:**
- [ ] Check Render logs for errors
- [ ] Verify scraping still works
- [ ] Review job quality

**Monthly:**
- [ ] Update dependencies
  ```bash
  pip install --upgrade playwright flask flask-cors gunicorn
  ```
- [ ] Test all platforms
- [ ] Review and optimize performance

**As Needed:**
- [ ] Update selectors if sites change structure
- [ ] Add new platforms
- [ ] Improve error handling

### Monitoring Metrics

Track in Render dashboard:
- Response time (should be < 5 minutes)
- Success rate (should be > 95%)
- Memory usage (should be stable)
- CPU usage (spikes during scraping are normal)

### Logging

**Enable detailed logging:**
```python
# In api.py, change:
logging.basicConfig(level=logging.DEBUG)
```

**Check logs:**
- Render dashboard → Logs tab
- Filter by error: Search for `❌`
- Filter by success: Search for `✅`

---

## Security Considerations

### ✅ Before Production

- [ ] Add rate limiting (optional)
  ```python
  from flask_limiter import Limiter
  limiter = Limiter(app, default_limits=["10 per hour"])
  ```

- [ ] Add API key authentication (optional)
  ```python
  API_KEY = os.environ.get('API_KEY')
  
  @app.before_request
  def check_api_key():
      if request.headers.get('X-API-Key') != API_KEY:
          return jsonify({'error': 'Unauthorized'}), 401
  ```

- [ ] Configure CORS properly
  ```python
  CORS(app, origins=['https://your-n8n-instance.com'])
  ```

- [ ] Set up HTTPS (Render does this automatically)

- [ ] Review and comply with:
  - [ ] Terms of Service of scraped sites
  - [ ] Robots.txt rules
  - [ ] Data privacy regulations

---

## Success Criteria

✅ **Deployment is successful when:**

1. Health check returns 200 OK
2. API scrapes at least 10 jobs
3. Response time < 5 minutes for 1 page
4. Jobs have full descriptions
5. No timeout errors in logs
6. n8n can call API successfully
7. Results match expected format

---

## Resources

**Render Documentation:**
- https://render.com/docs/web-services
- https://render.com/docs/yaml-spec
- https://render.com/docs/environment-variables

**Flask Documentation:**
- https://flask.palletsprojects.com/

**Playwright Documentation:**
- https://playwright.dev/python/

**n8n Documentation:**
- https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/

---

## Support

If you encounter issues:

1. **Check logs** - Most issues show up in logs
2. **Review this checklist** - Ensure all steps completed
3. **Test locally first** - Reproduce issue locally
4. **Search Render docs** - Common deployment issues
5. **Check site status** - Job sites may be down

**Common fixes:**
- Restart service on Render
- Clear build cache
- Re-deploy from dashboard
- Check environment variables

---

**Last Updated:** 2025-11-05
**Version:** 1.0.0
