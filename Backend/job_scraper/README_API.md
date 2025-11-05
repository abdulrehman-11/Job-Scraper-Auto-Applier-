# Job Scraper REST API

A production-ready REST API for scraping jobs from multiple job boards (SimplyHired, Talent.com, Glassdoor) designed for n8n automation workflows.

## 🚀 Features

- **Synchronous API**: Returns complete results (no webhooks needed)
- **Multi-platform scraping**: SimplyHired, Talent.com, Glassdoor
- **Full job descriptions**: Extracts complete job details
- **Duplicate detection**: Smart deduplication across platforms
- **24-hour filtering**: Only recent jobs
- **n8n compatible**: Response format optimized for n8n
- **Keep-alive mechanism**: Prevents timeout on long-running scrapes
- **Production ready**: Configured for Render deployment

## 📋 API Endpoints

### POST /api/scrape-jobs

Main endpoint for scraping jobs. Accepts optional parameters to customize the scrape.

**Request Body (all fields optional):**
```json
{
  "platform": "SimplyHired",
  "keywords": ["python developer", "data scientist"],
  "pages": 1,
  "location": "United States"
}
```

**Parameters:**
- `platform` (string, optional): Platform to scrape
  - `"SimplyHired"` - Only SimplyHired
  - `"Talent.com"` or `"Talent"` - Only Talent.com
  - `"Glassdoor"` - Only Glassdoor
  - `"all"` or `null` - All platforms (default)
- `keywords` (array, optional): Job search keywords (default: `["python developer"]`)
- `pages` (integer, optional): Pages to scrape per keyword (default: 1, max: 5)
- `location` (string, optional): Job location (default: `"United States"`)

**Response (Success - 200):**
```json
{
  "success": true,
  "total_jobs": 20,
  "scraped_at": "2025-11-04T22:30:00.000000",
  "jobs": [
    {
      "job_id": "simplyhired_2cff772b00f2",
      "title": "Machine Learning Engineer",
      "company": "GHI LLC",
      "location": "Dallas, TX",
      "job_type": "Full-time",
      "description": "Clean text without HTML...",
      "url": "https://...",
      "skills_required": "Python, PyTorch, Docker, SQL",
      "posted_date": "2025-11-03T23:30:32.958507",
      "salary": "$140,000 - $190,000 a year",
      "source_api": "SimplyHired",
      "fetched_at": "2025-11-04T22:30:38.419519"
    }
  ]
}
```

**Response (Error - 400/500):**
```json
{
  "success": false,
  "error": "Error message",
  "total_jobs": 0,
  "jobs": []
}
```

### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-04T22:30:00.000000",
  "scraping_status": "idle"
}
```

### GET /api/status

Get current scraping status.

**Response:**
```json
{
  "status": "running",
  "jobs_count": 15,
  "last_heartbeat": "2025-11-04T22:30:00.000000"
}
```

### GET /

API information endpoint.

## 🛠️ Local Development Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

1. **Clone the repository:**
```bash
cd Backend/job_scraper
```

2. **Install dependencies:**
```bash
pip install -r requirement.txt
```

3. **Install Playwright browsers:**
```bash
playwright install chromium
```

4. **Create .env file:**
```bash
cp .env.example .env
```

Edit `.env` and set:
```
DEBUG=False
PORT=5000
HEADLESS_MODE=True
```

### Running Locally

**Development mode:**
```bash
python api.py
```

**Production mode (with Gunicorn):**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 2 --timeout 600 api:app
```

### Testing the API

**Simple test:**
```bash
curl -X POST http://localhost:5000/api/scrape-jobs
```

**With parameters:**
```bash
curl -X POST http://localhost:5000/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "SimplyHired",
    "keywords": ["python developer"],
    "pages": 1,
    "location": "United States"
  }'
```

**PowerShell (Windows):**
```powershell
$body = @{
    platform = "SimplyHired"
    keywords = @("python developer")
    pages = 1
    location = "United States"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/scrape-jobs" -Method POST -Body $body -ContentType "application/json"
```

## 🚀 Deployment on Render

### Method 1: Using render.yaml (Recommended)

1. **Push code to GitHub**

2. **Create new Web Service on Render:**
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Create Web Service"

3. **Render will automatically:**
   - Install dependencies
   - Install Playwright with Chromium
   - Start the server with Gunicorn
   - Setup health checks

### Method 2: Manual Setup

1. **Create new Web Service on Render**

2. **Configure Build Command:**
```bash
pip install -r requirement.txt && playwright install --with-deps chromium
```

3. **Configure Start Command:**
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 600 --keep-alive 5 --log-level info api:app
```

4. **Set Environment Variables:**
```
PYTHON_VERSION=3.11.0
DEBUG=False
HEADLESS_MODE=True
MAX_PAGES_PER_KEYWORD=3
```

5. **Configure Health Check:**
   - Path: `/health`

### Important Render Settings

- **Instance Type**: Free or Starter (minimum)
- **Region**: Choose closest to your users
- **Auto-Deploy**: Enable for automatic deployments
- **Health Check Path**: `/health`

### Timeout Configuration

The API is configured to handle long-running scrapes:
- Gunicorn timeout: 600 seconds (10 minutes)
- Keep-alive: 5 seconds
- Heartbeat logs: Every 5 minutes

## 🔗 n8n Integration

### Setup in n8n

1. **Add HTTP Request Node**
   - Method: POST
   - URL: `https://your-app.onrender.com/api/scrape-jobs`
   - Body: JSON

2. **Configure Request Body:**
```json
{
  "platform": "{{ $json.platform }}",
  "keywords": {{ $json.keywords }},
  "pages": {{ $json.pages }},
  "location": "{{ $json.location }}"
}
```

3. **Set Timeout:**
   - Response timeout: 600000 (10 minutes)
   - This allows the scraper to complete

4. **Process Response:**
   - The response will contain `jobs` array
   - Use "Split In Batches" node to process jobs
   - Extract fields: `job_id`, `title`, `company`, etc.

### Example n8n Workflow

```
Scheduler (Daily 9 AM)
  ↓
HTTP Request (POST /api/scrape-jobs)
  ↓
Split In Batches (Process jobs array)
  ↓
Filter (Remove unwanted jobs)
  ↓
Send to Database/Email/Slack
```

## 📊 Monitoring

### Logs

**Check logs on Render:**
- Go to your service dashboard
- Click "Logs" tab
- Monitor for:
  - `🚀 Starting scraper`
  - `🔄 Still scraping...` (heartbeat)
  - `✅ Scraping completed`
  - `❌ Error` messages

**Local logs:**
- Console output
- `api.log` file
- `scraper.log` file

### Health Checks

**Render automatic health checks:**
- Pings `/health` endpoint every 60 seconds
- Service restarts if health check fails

**Manual health check:**
```bash
curl https://your-app.onrender.com/health
```

## 🐛 Troubleshooting

### Common Issues

**1. Timeout on Render**
- Check Gunicorn timeout is set to 600+ seconds
- Reduce `pages` parameter (try 1-2 pages)
- Reduce number of keywords

**2. Playwright Installation Fails**
- Ensure build command includes: `playwright install --with-deps chromium`
- Check Render build logs for errors

**3. CAPTCHA on Glassdoor**
- Glassdoor often shows CAPTCHAs
- Use only SimplyHired or Talent.com for automated scraping
- Or omit `"platform"` to skip Glassdoor on errors

**4. Empty Results**
- Check scraper logs for errors
- Verify keywords are valid
- Try different location

**5. n8n Timeout**
- Increase n8n HTTP Request timeout to 600000ms (10 minutes)
- Reduce scraping scope (fewer pages/keywords)

### Debug Mode

Enable debug logs locally:
```bash
export DEBUG=True
python api.py
```

## 🔒 Security Notes

- API has CORS enabled (adjust in production if needed)
- No authentication (add if needed)
- Rate limiting not implemented (consider adding)
- Scraping respects robots.txt and terms of service

## 📝 File Structure

```
job_scraper/
├── api.py                 # Flask REST API
├── Screp.py              # Job scraper core
├── config.py             # Configuration
├── requirement.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── Procfile             # Process file for Render
├── .env.example         # Environment variables template
├── README_API.md        # This file
├── jobs_output.json     # Output file (not used in API mode)
└── *.log               # Log files
```

## 🎯 Performance Tips

1. **Limit scope**: Use 1-2 keywords and 1-2 pages for faster results
2. **Single platform**: Scrape one platform at a time
3. **Cache results**: Store results in database for subsequent requests
4. **Schedule wisely**: Run during off-peak hours
5. **Monitor resources**: Check Render metrics

## 📄 License

MIT License - See LICENSE file

## 🤝 Support

For issues or questions:
1. Check logs first
2. Review troubleshooting section
3. Open GitHub issue with:
   - Error message
   - Request parameters
   - Render logs (if applicable)

---

**Built with ❤️ for automated job scraping**
