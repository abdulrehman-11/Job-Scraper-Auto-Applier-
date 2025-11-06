# 🚀 Render Deployment Guide - Job Scraper API

## Updated Configuration (Fixed Playwright Issue)

The Playwright installation issue has been resolved. Here's what was fixed:

### Files Created/Updated:
1. **`apt-packages`** - System dependencies for Chromium
2. **`render-build.sh`** - Custom build script
3. **`render.yaml`** - Updated Render configuration

---

## 📋 Render Dashboard Configuration

### **Fill in these fields on Render:**

| Field | Value |
|-------|-------|
| **Service Type** | Web Service |
| **Name** | `job-scraper-api` |
| **Language** | Python 3 |
| **Branch** | `main` |
| **Region** | Oregon (US West) |
| **Root Directory** | `job-link-dash/Backend/job_scraper` |
| **Build Command** | `chmod +x render-build.sh && ./render-build.sh` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 600 --keep-alive 5 --log-level info api:app` |

---

## 🔧 Build Command Explanation

The new build command does three things:

1. **Makes script executable**: `chmod +x render-build.sh`
2. **Runs the build script**: `./render-build.sh`
   - Installs Python packages from `requirement.txt`
   - Installs Chromium browser (without system deps - Render handles that via apt-packages)

### Why This Works:
- ❌ **Old approach**: `playwright install --with-deps` needed root access
- ✅ **New approach**: System dependencies via `apt-packages` file + Chromium-only install

---

## 🌐 Environment Variables (Optional)

Add these in Render Dashboard → Environment tab:

| Key | Value | Description |
|-----|-------|-------------|
| `PYTHON_VERSION` | `3.11.0` | Python version |
| `DEBUG` | `False` | Production mode |
| `HEADLESS_MODE` | `True` | Browser headless mode |
| `MAX_PAGES_PER_KEYWORD` | `3` | Limit scraping |
| `PLAYWRIGHT_BROWSERS_PATH` | `/opt/render/project/.cache/ms-playwright` | Browser cache location |

---

## 📝 Complete Copy-Paste Values

```
Root Directory:
job-link-dash/Backend/job_scraper

Build Command:
chmod +x render-build.sh && ./render-build.sh

Start Command:
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 600 --keep-alive 5 --log-level info api:app
```

---

## ✅ Deployment Steps

1. **Commit and Push Changes**:
   ```bash
   git add .
   git commit -m "Fix Playwright deployment for Render"
   git push origin main
   ```

2. **In Render Dashboard**:
   - Click "Create Web Service"
   - Connect your GitHub repository
   - Fill in the configuration above
   - Click "Create Web Service"

3. **Wait for Build** (~5-10 minutes first time)

4. **Test Your API**:
   ```bash
   curl https://your-app-name.onrender.com/health
   ```

---

## 🧪 Testing the Deployed API

### Health Check:
```bash
curl https://your-app-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-06T12:00:00.000000"
}
```

### Scrape Jobs:
```bash
curl -X POST https://your-app-name.onrender.com/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "simplyhired",
    "keywords": ["python developer"],
    "pages": 1,
    "location": "United States"
  }'
```

---

## 🐛 Troubleshooting

### Build Still Fails?

1. **Check Logs**: Go to Render Dashboard → Logs
2. **Common Issues**:
   - ❌ Script not executable → Make sure `chmod +x` is in build command
   - ❌ Module not found → Check `requirement.txt` exists
   - ❌ Browser error → Verify `apt-packages` file exists

### Playwright Errors in Runtime?

- Check environment variable: `PLAYWRIGHT_BROWSERS_PATH`
- Verify `apt-packages` includes all dependencies
- Check logs for missing system libraries

### Timeout Errors?

- Free tier has limitations
- Reduce `pages` parameter in API requests
- Consider upgrading to paid tier for better performance

---

## 💡 Key Changes Made

1. ✅ Created `apt-packages` file for system dependencies
2. ✅ Created `render-build.sh` build script
3. ✅ Updated `render.yaml` with correct configuration
4. ✅ Removed `--with-deps` flag from playwright install

---

## 📞 Next Steps

After successful deployment:
1. Note your API URL from Render dashboard
2. Update your frontend to use the new API URL
3. Test all endpoints thoroughly
4. Monitor logs for any issues

---

## 🎉 Success Indicators

You'll know deployment succeeded when:
- ✅ Build completes without errors
- ✅ Service status shows "Live"
- ✅ Health check endpoint returns 200
- ✅ Can scrape jobs successfully

---

**Need Help?** Check Render logs or refer to: https://render.com/docs/troubleshooting-deploys
