# 🚀 Render Deployment Guide - ChemPulse AI

Complete step-by-step guide to deploy your ChemPulse AI application on Render with PostgreSQL database.

---

## 📋 Prerequisites

1. **GitHub Account** - Push your code to GitHub
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Email Service** (Optional) - For alerts (Gmail, SendGrid, etc.)

---

## 🗂 Part 1: Prepare Your Code

### 1. Push to GitHub

```bash
cd c:\Users\acer\Desktop\fosse\ChemicalEquipmentVisualizer
git init
git add .
git commit -m "Initial commit - Ready for Render deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## 🗄 Part 2: Deploy Backend with PostgreSQL Database

### Step 1: Create PostgreSQL Database

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → Select **"PostgreSQL"**
3. Configure database:
   - **Name**: `chempulse-db`
   - **Database**: `chempulse`
   - **User**: `chempulse`
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 16 (or latest)
   - **Plan**: Free (or paid for better performance)
4. Click **"Create Database"**
5. ⏳ Wait for database to be provisioned (~2-3 minutes)
6. **Copy the "Internal Database URL"** - you'll need this!

### Step 2: Deploy Backend Web Service

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository:
   - Click **"Connect GitHub"** (authorize if needed)
   - Select your repository: `YOUR_USERNAME/YOUR_REPO`
3. Configure the service:
   - **Name**: `chempulse-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn backend.wsgi --log-file -`
   - **Plan**: Free (or paid)

4. **Set Environment Variables** (click "Advanced" → "Add Environment Variable"):

   | Key | Value |
   |-----|-------|
   | `PYTHON_VERSION` | `3.11.0` |
   | `SECRET_KEY` | Generate a secure key: [Django Secret Key Generator](https://djecrety.ir/) |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `chempulse-backend.onrender.com` (your backend URL) |
   | `DATABASE_URL` | Paste the Internal Database URL from Step 1 |
   | `CORS_ALLOWED_ORIGINS` | `https://chempulse-frontend.onrender.com` (your frontend URL) |
   | `EMAIL_HOST` | `smtp.gmail.com` (or your email provider) |
   | `EMAIL_PORT` | `587` |
   | `EMAIL_USE_TLS` | `True` |
   | `EMAIL_HOST_USER` | Your email address |
   | `EMAIL_HOST_PASSWORD` | Your app password (Gmail: [App Password](https://support.google.com/accounts/answer/185833)) |

5. Click **"Create Web Service"**
6. ⏳ Wait for deployment (~5-10 minutes)
7. Once deployed, you'll see a URL like: `https://chempulse-backend.onrender.com`

### Step 3: Verify Backend

- Visit: `https://chempulse-backend.onrender.com/api/equipment/`
- You should see an empty JSON array: `[]`
- Visit: `https://chempulse-backend.onrender.com/admin/` - Django admin should load

---

## 🌐 Part 3: Deploy Frontend (React/Vite)

### Step 1: Update Frontend API Configuration

Before deploying, update your frontend to use the production backend URL:

1. Open `web-frontend/src/` and find where the API base URL is defined
2. Update it to use environment variables:

Create `web-frontend/.env.production`:
```env
VITE_API_URL=https://chempulse-backend.onrender.com
```

Update your API calls to use:
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### Step 2: Deploy Frontend Web Service

1. In Render Dashboard, click **"New +"** → **"Static Site"**
2. Connect your repository (same as backend)
3. Configure the service:
   - **Name**: `chempulse-frontend`
   - **Branch**: `main`
   - **Root Directory**: `web-frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Set Environment Variables**:

   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://chempulse-backend.onrender.com` |

5. Click **"Create Static Site"**
6. ⏳ Wait for deployment (~3-5 minutes)
7. You'll get a URL like: `https://chempulse-frontend.onrender.com`

### Step 3: Update Backend CORS Settings

Go back to your backend service and update the `CORS_ALLOWED_ORIGINS` environment variable:
- Value: `https://chempulse-frontend.onrender.com`
- This allows your frontend to communicate with the backend

---

## ✅ Part 4: Final Verification

### Test Your Deployment

1. **Frontend**: Visit `https://chempulse-frontend.onrender.com`
2. **Upload Data**: Try uploading the sample CSV file
3. **Check API**: Verify data appears in the dashboard
4. **Test Alerts**: Configure thresholds and test email alerts
5. **Database Persistence**: Refresh the page - data should persist

### Common URLs

- Frontend: `https://chempulse-frontend.onrender.com`
- Backend API: `https://chempulse-backend.onrender.com/api/`
- Django Admin: `https://chempulse-backend.onrender.com/admin/`

---

## 🔧 Part 5: Post-Deployment Tasks

### Create Django Superuser

To access Django admin:

1. Go to Render Dashboard → Your backend service
2. Click **"Shell"** tab (top right)
3. Run:
```bash
python manage.py createsuperuser
```
4. Follow prompts to create admin account
5. Login at: `https://chempulse-backend.onrender.com/admin/`

### Enable Auto-Deploy (Optional)

Render automatically redeploys when you push to GitHub. To disable:
- Go to service settings → **"Auto-Deploy"** → Turn off

---

## 💰 Cost Breakdown (Free Tier)

| Service | Free Tier Limits |
|---------|------------------|
| PostgreSQL Database | 1GB storage, 97 hours/month* |
| Backend Web Service | 750 hours/month, sleeps after inactivity** |
| Frontend Static Site | 100GB bandwidth/month |

**Notes:**
- *Database hours reset monthly; upgrade to paid for 24/7 uptime
- **Free web services sleep after 15 min of inactivity; first request takes ~30s to wake up

---

## 🐛 Troubleshooting

### Build Fails

**Issue**: `permission denied: ./build.sh`
**Fix**: Make build.sh executable locally:
```bash
git update-index --chmod=+x backend/build.sh
git commit -m "Make build.sh executable"
git push
```

### Database Connection Error

**Issue**: `could not connect to server`
**Fix**: 
1. Verify `DATABASE_URL` is set correctly
2. Check database is in same region as backend
3. Ensure database is fully provisioned

### CORS Errors

**Issue**: Frontend can't access backend
**Fix**: 
1. Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL
2. No trailing slashes in URLs
3. Use `https://` (not `http://`)

### Static Files Not Loading

**Issue**: CSS/admin styles missing
**Fix**: 
1. Ensure `collectstatic` runs in `build.sh`
2. Check `STATIC_ROOT` is set in settings.py
3. Verify WhiteNoise is in middleware

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Render PostgreSQL Guide](https://render.com/docs/databases)

---

## 🎉 You're Live!

Your ChemPulse AI application is now running in the cloud with a production-grade PostgreSQL database! 🚀

**Next Steps:**
- Set up custom domain (optional)
- Configure monitoring and alerts
- Enable automatic backups for database
- Add CI/CD testing pipeline
