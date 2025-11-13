# ✅ DigitalOcean Deployment Checklist

Use this checklist to ensure a smooth deployment to DigitalOcean App Platform.

---

## 📦 Pre-Deployment

### Code Preparation
- [ ] All code committed to Git repository
- [ ] Repository pushed to GitHub/GitLab/Bitbucket
- [ ] `.env` file NOT committed (should be in `.gitignore`)
- [ ] All secrets removed from code
- [ ] `requirement.txt` is up to date

### Local Testing
- [ ] Docker installed and running
- [ ] Dockerfile builds successfully: `docker build -t job-scraper .`
- [ ] Docker container runs: `docker-compose up`
- [ ] Health endpoint accessible: `curl http://localhost:8080/health`
- [ ] Scraping endpoint works: Test with Postman or curl
- [ ] No errors in Docker logs

### Files Verification
- [ ] `Dockerfile` exists and configured
- [ ] `.dockerignore` exists
- [ ] `docker-compose.yml` exists (for local testing)
- [ ] `.env.example` exists with all variables documented
- [ ] `requirement.txt` has all dependencies
- [ ] `DIGITALOCEAN_DEPLOYMENT.md` guide reviewed

---

## 🚀 DigitalOcean Setup

### Account & Repository
- [ ] DigitalOcean account created and verified
- [ ] Payment method added
- [ ] Git provider connected (GitHub/GitLab/Bitbucket)
- [ ] Repository access granted to DigitalOcean

### App Creation
- [ ] App created on App Platform
- [ ] Correct repository selected
- [ ] Correct branch selected (usually `main`)
- [ ] Source directory set correctly
  - Standalone repo: `/`
  - Monorepo: `Backend/job_scraper`

### Build Configuration
- [ ] Dockerfile detected automatically
- [ ] Dockerfile path verified: `./Dockerfile`
- [ ] Build pack NOT selected (using Docker)
- [ ] HTTP port set to `8080`

---

## ⚙️ Environment Configuration

### Required Variables
- [ ] `PORT=8080` (auto-set by DigitalOcean)
- [ ] `DEBUG=False`
- [ ] `HEADLESS_MODE=True`
- [ ] `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright`

### Recommended Variables
- [ ] `LOG_LEVEL=INFO`
- [ ] `MAX_PAGES_PER_KEYWORD=3`
- [ ] `MAX_JOBS_GLASSDOOR=20`
- [ ] `DEFAULT_LOCATION=United States`
- [ ] `GUNICORN_TIMEOUT=600`
- [ ] `DIGITALOCEAN=true`

### Optional Variables (have defaults)
- [ ] `GUNICORN_WORKERS=1`
- [ ] `GUNICORN_THREADS=2`
- [ ] `MAX_KEYWORDS_PER_REQUEST=3`
- [ ] `MAX_PAGES_PER_REQUEST=5`

---

## 🏥 Health Check Configuration

- [ ] Health check enabled
- [ ] Path set to: `/health`
- [ ] Port set to: `8080`
- [ ] Initial delay: `60` seconds (important for browser installation)
- [ ] Timeout: `10` seconds
- [ ] Period: `30` seconds
- [ ] Success threshold: `1`
- [ ] Failure threshold: `3`

---

## 💰 Resource Allocation

### Instance Size
- [ ] Plan selected:
  - [ ] Basic ($5/month - 512MB) - Testing only
  - [ ] Professional ($12/month - 1GB) - **Recommended for production**
  - [ ] Higher tier - For heavy usage

### Scaling (Optional - Professional tier only)
- [ ] Auto-scaling configured if needed
- [ ] Min instances: `1`
- [ ] Max instances: `2-3`
- [ ] CPU threshold: `80%`

---

## 🚀 Deployment

### First Deployment
- [ ] Configuration reviewed
- [ ] "Create Resources" clicked
- [ ] Deployment started (monitor progress)
- [ ] Build logs checked for errors
- [ ] Wait for "Live" status (5-10 minutes first time)

### Deployment Success Indicators
- [ ] Status shows "Live" (green)
- [ ] No build errors in logs
- [ ] No runtime errors in logs
- [ ] URL accessible
- [ ] Health check passing

---

## 🧪 Post-Deployment Testing

### Basic Tests
- [ ] App URL accessible in browser
- [ ] Root endpoint works: `https://your-app.ondigitalocean.app/`
- [ ] Health check returns 200: `https://your-app.ondigitalocean.app/health`
- [ ] Browser available in health check response
- [ ] Status endpoint works: `https://your-app.ondigitalocean.app/api/status`

### Functional Tests
- [ ] Run test script: `python test_digitalocean_deployment.py YOUR_URL`
- [ ] All tests pass
- [ ] Scraping endpoint tested with actual request
- [ ] Jobs returned successfully
- [ ] Response time acceptable (<2 minutes for 1 page)

### Test Commands
```bash
# Health check
curl https://your-app.ondigitalocean.app/health

# Scraping test
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

## 📊 Monitoring Setup

### Basic Monitoring
- [ ] App Platform Insights tab reviewed
- [ ] CPU usage monitored
- [ ] Memory usage monitored
- [ ] Request count visible
- [ ] Error rate acceptable

### Alerts Configuration
- [ ] Alert for high CPU usage (>80%)
- [ ] Alert for high memory usage (>90%)
- [ ] Alert for failed deployments
- [ ] Alert for health check failures
- [ ] Email notifications configured

### Logging
- [ ] Runtime logs accessible
- [ ] Build logs accessible
- [ ] No recurring errors in logs
- [ ] Log level appropriate (INFO for production)

---

## 🔒 Security & Best Practices

### Security
- [ ] HTTPS enabled (automatic with App Platform)
- [ ] No secrets in code or logs
- [ ] Environment variables encrypted by platform
- [ ] `.env` in `.gitignore`
- [ ] No API keys hardcoded

### Performance
- [ ] Headless mode enabled for faster scraping
- [ ] Timeouts configured appropriately
- [ ] Rate limits considered
- [ ] Caching strategy planned (if needed)

### Reliability
- [ ] Health checks configured
- [ ] Automatic restarts enabled
- [ ] Error handling in code
- [ ] Graceful degradation implemented
- [ ] Monitoring and alerts set up

---

## 🔄 CI/CD Setup

### Automatic Deployments
- [ ] Auto-deploy on push enabled
- [ ] Correct branch configured for auto-deploy
- [ ] Build notifications enabled
- [ ] Deployment notifications enabled

### Testing Pipeline
- [ ] Tests run before deployment (if applicable)
- [ ] Deployment rollback plan in place
- [ ] Staging environment considered (optional)

---

## 📝 Documentation

### Internal Documentation
- [ ] Deployment process documented
- [ ] Environment variables documented
- [ ] API endpoints documented
- [ ] Troubleshooting guide available
- [ ] Team notified of deployment

### External Documentation
- [ ] API documentation updated (if public)
- [ ] Frontend team notified of API URL
- [ ] Integration partners notified

---

## 🎯 Final Verification

### Production Readiness
- [ ] All tests passing
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Health check consistently passing
- [ ] Monitoring working
- [ ] Alerts configured
- [ ] Team trained on monitoring
- [ ] Rollback plan documented
- [ ] Backup strategy in place (if storing data)

### Go-Live Checklist
- [ ] Production URL noted and saved
- [ ] DNS configured (if using custom domain)
- [ ] Frontend connected to API
- [ ] Integration tests passed
- [ ] Load testing done (if expecting high traffic)
- [ ] Support team ready
- [ ] Documentation complete

---

## 📞 Support Resources

- **DigitalOcean Docs:** https://docs.digitalocean.com/products/app-platform/
- **Community:** https://www.digitalocean.com/community
- **Support Tickets:** https://cloud.digitalocean.com/support
- **Status Page:** https://status.digitalocean.com/

---

## ✅ Deployment Complete!

If all items are checked:
- 🎉 **Congratulations!** Your Job Scraper API is live on DigitalOcean
- 📊 Monitor the Insights tab regularly
- 🔍 Check logs for any issues
- 📈 Plan for scaling as usage grows

**Next Steps:**
1. Monitor initial usage
2. Optimize based on metrics
3. Set up regular backups (if needed)
4. Plan for feature updates
5. Consider adding rate limiting
6. Implement API authentication (if needed)

---

**Date Deployed:** _________________

**Deployed By:** _________________

**Production URL:** _________________

**Notes:** _________________
