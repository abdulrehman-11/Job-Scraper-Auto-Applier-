# 🚀 Quick Reference Card - DigitalOcean Deployment

**Pin this for quick access during deployment!**

---

## ⚡ One-Line Deploy

```bash
# 1. Push code
git add . && git commit -m "Deploy to DigitalOcean" && git push

# 2. Go to: https://cloud.digitalocean.com/apps
# 3. Create App → Select Repo → Deploy!
```

---

## 🔑 Essential Environment Variables

```bash
HEADLESS_MODE=True
DEBUG=False  
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
```

**That's it!** Everything else has defaults.

---

## 🧪 Quick Test Commands

```bash
# Health Check
curl https://YOUR-APP.ondigitalocean.app/health

# Test Scraping
curl -X POST https://YOUR-APP.ondigitalocean.app/api/scrape-jobs \
  -H "Content-Type: application/json" \
  -d '{"keywords":["python developer"],"pages":1}'

# Automated Test
python test_digitalocean_deployment.py https://YOUR-APP.ondigitalocean.app
```

---

## 📊 Health Check Response (Expected)

```json
{
  "status": "healthy",
  "browser": {
    "available": true,
    "path": "/ms-playwright"
  }
}
```

---

## 🏥 Health Check Settings

| Setting | Value |
|---------|-------|
| Path | `/health` |
| Port | `8080` |
| Initial Delay | `60s` |
| Timeout | `10s` |
| Period | `30s` |

---

## 💰 Pricing Quick Guide

- **$5/mo** - Testing (512MB RAM)
- **$12/mo** - Production (1GB RAM) ⭐ Recommended
- **$24/mo** - High traffic (2GB RAM)

---

## 🆘 Troubleshooting Shortcuts

| Problem | Quick Fix |
|---------|-----------|
| Browser not found | Check `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` |
| Timeout | Increase plan or reduce `MAX_PAGES_PER_KEYWORD=2` |
| Build fails | Check Runtime Logs in DO dashboard |
| Health check fails | Wait 60s after deploy, then check logs |

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Container config |
| `QUICKSTART_DIGITALOCEAN.md` | 10-min deploy guide |
| `DIGITALOCEAN_DEPLOYMENT.md` | Full guide |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step checklist |
| `test_digitalocean_deployment.py` | Test script |

---

## 🔗 Quick Links

- **Deploy:** https://cloud.digitalocean.com/apps
- **Docs:** https://docs.digitalocean.com/products/app-platform/
- **Status:** https://status.digitalocean.com/

---

## ✅ Pre-Deploy Checklist

- [ ] Code pushed to Git
- [ ] Dockerfile exists
- [ ] Environment variables ready
- [ ] Health check path: `/health`
- [ ] Port: `8080`

---

## 📞 Emergency Commands

```bash
# View logs (if deployed)
doctl apps logs YOUR_APP_ID

# Rebuild
doctl apps create-deployment YOUR_APP_ID

# Check status
curl https://YOUR-APP.ondigitalocean.app/health
```

---

**Keep this handy during deployment! 📌**

For full guide, see: `DIGITALOCEAN_DEPLOYMENT.md`
