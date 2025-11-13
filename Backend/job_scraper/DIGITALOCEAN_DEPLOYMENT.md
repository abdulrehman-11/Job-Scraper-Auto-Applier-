# 🚀 DigitalOcean Deployment Guide - Job Scraper API

Complete guide to deploy the Job Scraper API to DigitalOcean App Platform.

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Option A: App Platform (Recommended)](#option-a-app-platform-recommended)
4. [Option B: Droplet with Docker](#option-b-droplet-with-docker)
5. [Environment Variables](#environment-variables)
6. [Testing Deployment](#testing-deployment)
7. [Monitoring & Scaling](#monitoring--scaling)
8. [Troubleshooting](#troubleshooting)

---

## ✅ Prerequisites

Before deploying, ensure you have:

- [ ] DigitalOcean account ([Sign up](https://www.digitalocean.com/))
- [ ] Git repository (GitHub, GitLab, or Bitbucket)
- [ ] Docker installed locally (for testing)
- [ ] Basic knowledge of containerized applications

---

## 🎯 Deployment Options

### Option A: App Platform (Recommended)
**Best for:** Quick deployment, automatic scaling, managed infrastructure
- ✅ No server management
- ✅ Automatic SSL/HTTPS
- ✅ Built-in CI/CD
- ✅ Easy scaling
- 💰 Starting at $5/month

### Option B: Droplet with Docker
**Best for:** Full control, cost optimization for high traffic
- ✅ Complete control over environment
- ✅ Can run multiple services
- ⚠️ Requires manual management
- 💰 Starting at $6/month

---

## 🚀 Option A: App Platform (Recommended)

### Step 1: Push Code to Git Repository

```bash
# Navigate to your project
cd Backend/job_scraper

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit - DigitalOcean ready"

# Push to your repository
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### Step 2: Create App Platform Application

1. **Go to DigitalOcean Dashboard**
   - Navigate to [App Platform](https://cloud.digitalocean.com/apps)
   - Click **"Create App"**

2. **Connect Your Repository**
   - Select your Git provider (GitHub/GitLab/Bitbucket)
   - Authorize DigitalOcean to access your repository
   - Select your repository and branch (e.g., `main`)

3. **Configure Your App**
   - **App Name:** `job-scraper-api` (or your preferred name)
   - **Region:** Choose closest to your users
   - **Branch:** `main` (or your deployment branch)
   - **Source Directory:** `Backend/job_scraper` (if in monorepo) or `/` (if standalone)

### Step 3: Configure Build & Deploy Settings

#### Build Configuration
```yaml
# App Platform will auto-detect Dockerfile
# Or manually configure:

Build Command: (leave empty - Docker handles this)
Run Command: (leave empty - Docker CMD handles this)

Dockerfile Path: ./Dockerfile
```

#### Resource Settings
- **Plan:** Basic ($5/month)
  - 512 MB RAM / 0.5 vCPU
  - Good for testing and light usage
  
- **Professional ($12/month)** - Recommended for production
  - 1 GB RAM / 1 vCPU
  - Better for concurrent scraping requests

### Step 4: Configure Environment Variables

In the App Platform dashboard, add these environment variables:

| Variable | Value | Required |
|----------|-------|----------|
| `PORT` | `8080` | ✅ Yes (auto-set by DO) |
| `DEBUG` | `False` | ✅ Yes |
| `HEADLESS_MODE` | `True` | ✅ Yes |
| `PLAYWRIGHT_BROWSERS_PATH` | `/ms-playwright` | ✅ Yes |
| `LOG_LEVEL` | `INFO` | ⚪ Optional |
| `MAX_PAGES_PER_KEYWORD` | `3` | ⚪ Optional |
| `MAX_JOBS_GLASSDOOR` | `20` | ⚪ Optional |
| `DEFAULT_LOCATION` | `United States` | ⚪ Optional |
| `DIGITALOCEAN` | `true` | ⚪ Optional |
| `GUNICORN_WORKERS` | `1` | ⚪ Optional |
| `GUNICORN_TIMEOUT` | `600` | ⚪ Optional |

### Step 5: Configure Health Check

- **Path:** `/health`
- **Port:** `8080`
- **Initial Delay:** 60 seconds
- **Timeout:** 10 seconds
- **Period:** 30 seconds
- **Success Threshold:** 1
- **Failure Threshold:** 3

### Step 6: Deploy!

1. Click **"Next"** to review configuration
2. Review all settings
3. Click **"Create Resources"**
4. Wait for deployment (5-10 minutes for first deploy)

### Step 7: Verify Deployment

Once deployed, you'll get a URL like: `https://job-scraper-api-xxxxx.ondigitalocean.app`

Test the endpoints:

```bash
# Health check
curl https://your-app-url.ondigitalocean.app/health

# Root endpoint
curl https://your-app-url.ondigitalocean.app/

# Test scraping (POST request)
curl -X POST https://your-app-url.ondigitalocean.app/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "SimplyHired",
    "keywords": ["python developer"],
    "pages": 1,
    "location": "United States"
  }'
```

---

## 🐳 Option B: Droplet with Docker

### Step 1: Create Droplet

1. Go to [DigitalOcean Droplets](https://cloud.digitalocean.com/droplets)
2. Click **"Create Droplet"**
3. Choose:
   - **Image:** Docker on Ubuntu 22.04
   - **Plan:** Basic ($6/month - 1GB RAM)
   - **Region:** Closest to your users
   - **Authentication:** SSH key (recommended) or password
4. Click **"Create Droplet"**

### Step 2: Connect to Droplet

```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP
```

### Step 3: Deploy Application

```bash
# Clone your repository
git clone YOUR_REPO_URL
cd YOUR_REPO_NAME/Backend/job_scraper

# Create .env file
cp .env.example .env
nano .env  # Edit with your configuration

# Build and run with Docker Compose
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

### Step 4: Configure Firewall

```bash
# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8080/tcp
ufw enable
```

### Step 5: Set Up Reverse Proxy (Optional - for HTTPS)

```bash
# Install Nginx
apt update
apt install nginx certbot python3-certbot-nginx -y

# Create Nginx config
cat > /etc/nginx/sites-available/job-scraper << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600s;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/job-scraper /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Optional: Get SSL certificate (if you have a domain)
certbot --nginx -d YOUR_DOMAIN
```

---

## 🔐 Environment Variables

### Required Variables

```bash
PORT=8080                           # Application port
DEBUG=False                         # Never True in production
HEADLESS_MODE=True                  # Must be True for production
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright  # Browser installation path
```

### Optional Variables (with defaults)

```bash
# Scraping Configuration
MAX_PAGES_PER_KEYWORD=3            # Pages to scrape per keyword
MAX_JOBS_GLASSDOOR=20              # Max jobs from Glassdoor
DEFAULT_LOCATION="United States"   # Default search location

# Performance
GUNICORN_WORKERS=1                 # Number of worker processes
GUNICORN_THREADS=2                 # Threads per worker
GUNICORN_TIMEOUT=600               # Request timeout (10 minutes)

# Logging
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR

# Platform
DIGITALOCEAN=true                  # Platform identification
```

---

## 🧪 Testing Deployment

Use the provided test script:

```bash
# Local testing
python test_digitalocean_deployment.py

# Or manually test
curl -X GET https://your-app-url.ondigitalocean.app/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-11-13T...",
  "browser": {
    "available": true,
    "path": "/ms-playwright",
    "message": "Chromium browser found"
  },
  "environment": {
    "playwright_path": "/ms-playwright",
    "python_version": "3.11.x",
    "platform": "DigitalOcean",
    "port": "8080"
  }
}
```

### Test Scraping Endpoint

```python
import requests
import json

url = "https://your-app-url.ondigitalocean.app/api/scrape-jobs"
payload = {
    "platform": "SimplyHired",
    "keywords": ["python developer"],
    "pages": 1,
    "location": "United States"
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

---

## 📊 Monitoring & Scaling

### App Platform Monitoring

1. **Access Metrics:**
   - Go to your app in App Platform
   - Click **"Insights"** tab
   - View CPU, Memory, Bandwidth usage

2. **View Logs:**
   - Click **"Runtime Logs"** tab
   - Real-time log streaming
   - Search and filter logs

3. **Scaling:**
   - Go to **"Settings"** → **"Resources"**
   - Increase container size if needed
   - Add horizontal scaling (multiple instances)

### Alerts Setup

1. Go to **Monitoring** → **Alerts**
2. Create alerts for:
   - High CPU usage (>80%)
   - High memory usage (>90%)
   - Error rate threshold
   - Response time threshold

---

## 🔧 Troubleshooting

### Issue: Browser Not Found

**Error:** `Browser not found` in health check

**Solution:**
```bash
# Verify Dockerfile includes browser installation
# Check environment variable
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Rebuild the container
docker-compose up -d --build
```

### Issue: Timeout Errors

**Error:** `504 Gateway Timeout`

**Solution:**
1. Increase `GUNICORN_TIMEOUT` to 900 (15 minutes)
2. Reduce `MAX_PAGES_PER_KEYWORD` to 2
3. Upgrade to higher plan (more CPU/RAM)

### Issue: Memory Issues

**Error:** Container crashes or OOM errors

**Solution:**
1. Upgrade to Professional plan (1GB+ RAM)
2. Reduce concurrent scraping
3. Set `GUNICORN_WORKERS=1` (single worker uses less memory)

### Issue: Slow Scraping

**Problem:** Requests taking too long

**Solution:**
1. Use `HEADLESS_MODE=True` (faster)
2. Reduce pages per request
3. Consider caching results
4. Upgrade to better plan

### Issue: Health Check Failing

**Error:** Health check returns unhealthy

**Solution:**
```bash
# Check logs for errors
docker-compose logs -f

# Test health endpoint locally
curl http://localhost:8080/health

# Verify Playwright installation
docker exec -it job-scraper-api playwright install chromium
```

---

## 📚 Additional Resources

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Docker Documentation](https://docs.docker.com/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Flask Production Best Practices](https://flask.palletsprojects.com/en/2.3.x/deploying/)

---

## 💡 Production Best Practices

1. **Security:**
   - Never commit `.env` files
   - Use strong secrets for API keys
   - Enable HTTPS (automatic with App Platform)
   - Regular security updates

2. **Performance:**
   - Enable caching where appropriate
   - Monitor resource usage
   - Scale based on traffic patterns
   - Use CDN for static assets

3. **Reliability:**
   - Set up monitoring and alerts
   - Regular backups
   - Implement rate limiting
   - Use health checks

4. **Cost Optimization:**
   - Start with Basic plan, scale as needed
   - Monitor resource usage
   - Consider reserved instances for predictable traffic
   - Clean up unused resources

---

## 🎉 Success!

Your Job Scraper API is now running on DigitalOcean! 

**Next Steps:**
- Connect your frontend application
- Set up monitoring and alerts
- Configure custom domain (optional)
- Implement rate limiting
- Add authentication if needed

**Questions or Issues?**
- Check the troubleshooting section above
- Review DigitalOcean documentation
- Check application logs

Happy scraping! 🚀
