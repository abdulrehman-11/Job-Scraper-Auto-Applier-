# 🚀 Quick Start Guide - Job Scraper API

Get your job scraper API running in 5 minutes!

## Local Testing (2 minutes)

### Step 1: Install Dependencies
```bash
cd Backend/job_scraper
pip install -r requirement.txt
playwright install chromium
```

### Step 2: Run the API
```bash
python api.py
```

You should see:
```
🚀 Starting Job Scraper API on port 5000
 * Running on http://0.0.0.0:5000
```

### Step 3: Test It
Open a new terminal and run:

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET
```

**Linux/Mac/Git Bash:**
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T...",
  "scraping_status": "idle"
}
```

### Step 4: Scrape Jobs
**PowerShell:**
```powershell
$body = @{
    platform = "SimplyHired"
    keywords = @("python developer")
    pages = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/scrape-jobs" -Method POST -Body $body -ContentType "application/json"
```

**Bash:**
```bash
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{"platform": "SimplyHired", "keywords": ["python developer"], "pages": 1}'
```

⏱️ This will take 1-3 minutes. You should see jobs data returned!

---

## Deploy to Render (3 minutes)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Job Scraper API"
git push origin main
```

### Step 2: Create Render Service
1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repo
5. Render detects `render.yaml` automatically
6. Click **"Create Web Service"**

### Step 3: Wait for Deploy
Watch the build logs. It takes 2-3 minutes.

### Step 4: Test Deployed API
Replace `YOUR_APP_URL` with your Render URL:

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "https://YOUR_APP_URL.onrender.com/health" -Method GET
```

**Bash:**
```bash
curl https://YOUR_APP_URL.onrender.com/health
```

**Test scraping:**
```powershell
$body = @{
    platform = "SimplyHired"
    keywords = @("python developer")
    pages = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://YOUR_APP_URL.onrender.com/api/scrape-jobs" -Method POST -Body $body -ContentType "application/json"
```

✅ **Done!** Your API is live!

---

## n8n Integration (1 minute)

### Add HTTP Request Node
1. **Method:** POST
2. **URL:** `https://YOUR_APP_URL.onrender.com/api/scrape-jobs`
3. **Body (JSON):**
```json
{
  "platform": "SimplyHired",
  "keywords": ["python developer"],
  "pages": 1,
  "location": "United States"
}
```
4. **Options → Timeout:** `600000` (10 minutes)

### Test in n8n
Click **"Execute Node"** and wait 1-3 minutes for results!

---

## What You Get

Every API call returns jobs in this format:

```json
{
  "success": true,
  "total_jobs": 20,
  "scraped_at": "2025-11-05T12:30:00",
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
      "fetched_at": "2025-11-05T12:30:00"
    }
  ]
}
```

---

## Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `platform` | string | `null` (all) | `"SimplyHired"`, `"Talent.com"`, `"Glassdoor"`, or `"all"` |
| `keywords` | array | `["python developer"]` | Job search keywords |
| `pages` | integer | `1` | Pages to scrape (max 5) |
| `location` | string | `"United States"` | Job location |

---

## Tips

✅ **For faster results:**
- Use 1 page
- Use 1-2 keywords
- Use single platform

✅ **For more jobs:**
- Use 3-5 pages
- Use multiple keywords
- Use "all" platforms

⚠️ **Be aware:**
- More pages = longer wait time
- Glassdoor may have CAPTCHAs
- Free Render tier spins down after inactivity

---

## Troubleshooting

### "Connection refused" error
→ Make sure API is running: `python api.py`

### "Timeout" error
→ Increase timeout or reduce pages/keywords

### "Empty results"
→ Check logs: `api.log` and `scraper.log`

### Render service sleeping (Free tier)
→ First request takes 30+ seconds (cold start)

---

## Next Steps

📖 **Read the full documentation:**
- [README_API.md](README_API.md) - Complete API documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide

🧪 **Run the test suite:**
```bash
python test_api.py
```

🔧 **Customize configuration:**
- Edit `config.py` for default settings
- Add `.env` file for environment variables

---

## Support

**Need help?**
1. Check logs: `api.log` and `scraper.log`
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
3. Open GitHub issue with error details

**Working?** ⭐ Star the repo!

---

**Built with ❤️ for automated job scraping**
