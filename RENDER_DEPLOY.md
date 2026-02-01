# 🚀 Quick Render Deployment Checklist

## ✅ Pre-Deployment (Already Done!)

- [x] Updated `settings.py` for production (PostgreSQL, WhiteNoise, security)
- [x] Added `dj-database-url` to `requirements.txt`
- [x] Created `build.sh` script
- [x] Updated frontend to use environment variables
- [x] Created `.env.production` for frontend

---

## 📝 Step-by-Step Deployment

### 1️⃣ Push Code to GitHub (5 minutes)

```bash
cd ChemicalEquipmentVisualizer
git init
git add .
git commit -m "Ready for Render deployment"
git branch -M main

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

### 2️⃣ Create PostgreSQL Database (3 minutes)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Fill in:
   - Name: `chempulse-db`
   - Database: `chempulse`
   - Region: Choose closest
4. Click **Create Database**
5. **COPY the "Internal Database URL"** when ready

---

### 3️⃣ Deploy Backend (10 minutes)

1. Click **New +** → **Web Service**
2. Connect your GitHub repo
3. Configure:
   - Name: `chempulse-backend`
   - Root Directory: `backend`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn backend.wsgi --log-file -`

4. **Add Environment Variables**:
   ```
   PYTHON_VERSION = 3.11.0
   SECRET_KEY = [Generate at djecrety.ir]
   DEBUG = False
   ALLOWED_HOSTS = chempulse-backend.onrender.com
   DATABASE_URL = [Paste from Step 2]
   CORS_ALLOWED_ORIGINS = https://chempulse-frontend.onrender.com
   ```

5. Click **Create Web Service**
6. Wait for deployment ✅

---

### 4️⃣ Deploy Frontend (5 minutes)

1. Click **New +** → **Static Site**
2. Connect same GitHub repo
3. Configure:
   - Name: `chempulse-frontend`
   - Root Directory: `web-frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`

4. **Add Environment Variable**:
   ```
   VITE_API_URL = https://chempulse-backend.onrender.com
   ```

5. Click **Create Static Site**
6. Wait for deployment ✅

---

### 5️⃣ Final Steps (2 minutes)

1. **Update Backend CORS**: 
   - Go to backend service → Environment
   - Update `CORS_ALLOWED_ORIGINS` with actual frontend URL

2. **Test Your App**:
   - Visit frontend URL
   - Upload sample CSV
   - Check data persists!

3. **Create Admin User** (Optional):
   - Backend service → Shell tab
   - Run: `python manage.py createsuperuser`

---

## 🎯 Your Live URLs

- **Frontend**: `https://chempulse-frontend.onrender.com`
- **Backend API**: `https://chempulse-backend.onrender.com/api/`
- **Admin Panel**: `https://chempulse-backend.onrender.com/admin/`

---

## ⚠️ Important Notes

- **Free Tier**: Services sleep after 15 min of inactivity
- **First Load**: May take 30 seconds to wake up
- **Database**: 1GB storage, 97 hours/month on free tier
- **Auto-Deploy**: Enabled by default on git push

---

## 🐛 Quick Fixes

**Build.sh Permission Error**:
```bash
git update-index --chmod=+x backend/build.sh
git commit -m "Fix permissions"
git push
```

**CORS Errors**: 
- Use `https://` (not `http://`)
- No trailing slashes in URLs

**Database Connection**: 
- Verify DATABASE_URL is correct
- Check same region as backend

---

## 📚 Full Guide

See `DEPLOYMENT_GUIDE.md` for detailed instructions and troubleshooting.

---

**Total Time**: ~25 minutes ⏱️
