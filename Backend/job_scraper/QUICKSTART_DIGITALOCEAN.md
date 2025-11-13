# 🚀 Quick Start - DigitalOcean Deployment

Get your Job Scraper API deployed to DigitalOcean in under 10 minutes!

---

## ⚡ Fast Track Deployment

### 1️⃣ Local Testing (Optional but Recommended)

```bash
# Navigate to project
cd Backend/job_scraper

# Test with Docker locally
docker-compose up --build

# In another terminal, test
curl http://localhost:8080/health
```

### 2️⃣ Push to Git

```bash
git add .
git commit -m "Ready for DigitalOcean deployment"
git push origin main
```

### 3️⃣ Deploy to DigitalOcean

1. **Go to:** https://cloud.digitalocean.com/apps
2. **Click:** "Create App"
3. **Select:** Your repository
4. **Configure:**
   - Source Directory: `Backend/job_scraper` (or `/` if standalone)
   - Dockerfile Path: `./Dockerfile`
   - Port: `8080`

5. **Set Environment Variables:**
   ```
   HEADLESS_MODE=True
   DEBUG=False
   PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
   DIGITALOCEAN=true
   ```

6. **Set Health Check:**
   - Path: `/health`
   - Port: `8080`

7. **Click:** "Create Resources"

### 4️⃣ Test Deployment

```bash
# After deployment, test with your URL
python test_digitalocean_deployment.py https://your-app.ondigitalocean.app
```

---

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Container configuration |
| `docker-compose.yml` | Local testing |
| `.env.example` | Environment variables template |
| `DIGITALOCEAN_DEPLOYMENT.md` | Complete deployment guide |
| `test_digitalocean_deployment.py` | Deployment verification |

---

## 📋 Minimum Environment Variables

Only 3 variables are **required**:

```bash
HEADLESS_MODE=True
DEBUG=False
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
```

Everything else has sensible defaults!

---

## 🧪 Test Endpoints

After deployment, your API will be available at:

```
https://your-app-name.ondigitalocean.app
```

**Test commands:**

```bash
# Health check
curl https://your-app.ondigitalocean.app/health

# API info
curl https://your-app.ondigitalocean.app/

# Scrape jobs (POST request)
curl -X POST https://your-app.ondigitalocean.app/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "SimplyHired",
    "keywords": ["python developer"],
    "pages": 1,
    "location": "United States"
  }'
```

---

## 💰 Pricing

- **Basic Plan:** $5/month (512MB RAM) - Good for testing
- **Professional:** $12/month (1GB RAM) - Recommended for production
- **Custom:** Scale as needed

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Browser not found | Check `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` |
| Timeout errors | Increase plan or reduce `MAX_PAGES_PER_KEYWORD` |
| Build fails | Check Dockerfile syntax, view build logs |
| Health check fails | Wait 60s after deploy, check runtime logs |

---

## 📚 Need More Help?

- **Full Guide:** See `DIGITALOCEAN_DEPLOYMENT.md`
- **DigitalOcean Docs:** https://docs.digitalocean.com/products/app-platform/
- **Support:** Check DigitalOcean community forums

---

## ✅ Checklist

- [ ] Code pushed to Git repository
- [ ] DigitalOcean account created
- [ ] App created on App Platform
- [ ] Environment variables configured
- [ ] Health check configured
- [ ] First deployment successful
- [ ] Health endpoint returns 200
- [ ] Scraping endpoint tested
- [ ] Monitoring set up

**You're ready to go! 🎉**
