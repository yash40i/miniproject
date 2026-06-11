# DEPLOYMENT GUIDE - Resume-Insight AI

## Overview
Deployment Stack:
- **Frontend**: Vercel (Next.js optimized)
- **Backend**: Railway (FastAPI + Python)
- **Database**: PostgreSQL (Railway managed)
- **Domain**: Your custom domain

---

## Phase 1: Prepare for Deployment

### Step 1.1: Update Backend Configuration for Production

**Location**: `src/database.py`

Update the database URL to support both SQLite (dev) and PostgreSQL (prod):

```python
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./analysis.db")

# For PostgreSQL on production
if DATABASE_URL.startswith("postgresql"):
    # No changes needed, SQLAlchemy handles it
    pass

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
```

### Step 1.2: Update Backend CORS Configuration

**Location**: `backend/main.py`

Update CORS to accept production domain:

```python
import os

ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 1.3: Environment Variables

Create `.env.production` in project root with production secrets:

```
# Database - Railway PostgreSQL
DATABASE_URL=postgresql://user:password@host:port/dbname

# Backend
SECRET_KEY=your-long-random-secret-key-at-least-32-chars
ALGORITHM=HS256

# Google OAuth - Production Credentials
GOOGLE_CLIENT_ID=your-production-google-client-id
GOOGLE_CLIENT_SECRET=your-production-google-client-secret

# CORS
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Environment
ENVIRONMENT=production
DEBUG=false
```

---

## Phase 2: Set Up Database (PostgreSQL on Railway)

### Step 2.1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub (recommended)
3. Create new project

### Step 2.2: Add PostgreSQL Service
1. In Railway dashboard, click "New Service"
2. Select "PostgreSQL"
3. Railway will provision a PostgreSQL instance
4. Copy the connection string (DATABASE_URL)
5. Save it securely

### Step 2.3: Run Database Migrations
When backend starts on Railway, it will automatically create tables using SQLAlchemy. First deployment will initialize the database.

---

## Phase 3: Deploy Backend to Railway

### Step 3.1: Push Code to GitHub
```powershell
git init
git add .
git commit -m "Initial commit: Auth system ready for deployment"
git remote add origin https://github.com/your-username/res_project.git
git branch -M main
git push -u origin main
```

### Step 3.2: Connect GitHub to Railway
1. In Railway dashboard, click "New Project"
2. Select "GitHub Repo"
3. Select your `res_project` repository
4. Railway auto-detects it's a Python project

### Step 3.3: Configure Environment Variables in Railway
1. Go to Variables tab
2. Add from `.env.production`:
   - `DATABASE_URL` (from PostgreSQL service)
   - `SECRET_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `CORS_ORIGINS`
   - `ENVIRONMENT=production`

### Step 3.4: Configure Build & Start
Create `Procfile` in project root:
```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Railway will:
1. Detect `requirements.txt`
2. Install dependencies
3. Run the Procfile command
4. Assign a public URL (e.g., `your-project.up.railway.app`)

---

## Phase 4: Deploy Frontend to Vercel

### Step 4.1: Update API URL
**File**: `frontend/.env.production`

```
NEXT_PUBLIC_API_URL=https://your-railway-backend-url.up.railway.app
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-production-google-client-id
```

### Step 4.2: Connect to Vercel
1. Go to https://vercel.com
2. Click "New Project"
3. Select "Import Git Repository"
4. Choose your GitHub repo

### Step 4.3: Configure Build Settings
Vercel auto-detects Next.js:
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm ci`

### Step 4.4: Add Environment Variables in Vercel
1. Go to Settings → Environment Variables
2. Add:
   - `NEXT_PUBLIC_API_URL=https://your-railway-backend-url.up.railway.app`
   - `NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-production-google-client-id`

### Step 4.5: Deploy
Push to main branch or click "Deploy" in Vercel dashboard.

---

## Phase 5: Configure Custom Domain

### Step 5.1: Vercel Domain Setup
1. In Vercel project settings → Domains
2. Add your custom domain
3. Update DNS records (Vercel provides CNAME records)
4. Wait for DNS propagation (5-30 minutes)

### Step 5.2: Railway Domain Setup
Railway backend will have URL like `your-project.up.railway.app` - no custom domain needed for API (not user-facing).

---

## Phase 6: Update Google OAuth for Production

### Step 6.1: Create Production Google OAuth Credentials
1. Go to https://console.cloud.google.com
2. Create new OAuth 2.0 credential (Web application)
3. **Authorized JavaScript origins**:
   - `https://your-domain.com`
   - `https://www.your-domain.com`
4. **Authorized redirect URIs**:
   - `https://your-domain.com/api/auth/callback`
5. Copy Client ID and Secret
6. Add to Railway and Vercel environment variables

### Step 6.2: Verify Google Sign-In Works
1. Visit https://your-domain.com/signup
2. Click "Sign in with Google"
3. Complete Google authentication
4. Verify you're redirected to dashboard
5. Check localStorage has `auth_token`

---

## Phase 7: Testing Checklist

- [ ] Backend deployed and responding at `https://your-railway-backend-url.up.railway.app/docs`
- [ ] Frontend deployed at `https://your-domain.com`
- [ ] Email/password signup works
- [ ] Email/password login works
- [ ] Google OAuth sign-in works
- [ ] Token persists after page refresh
- [ ] Logout clears token
- [ ] Protected pages redirect to login when logged out
- [ ] Database queries work (user records created)
- [ ] API errors display properly in UI

---

## Common Issues & Fixes

### Issue: "Failed to decode Google token"
**Solution**: Verify `GOOGLE_CLIENT_SECRET` is correct in Railway

### Issue: CORS error "Origin not allowed"
**Solution**: Check `CORS_ORIGINS` in Railway matches your domain

### Issue: "Cannot reach backend"
**Solution**: Check Railway URL in Vercel environment variables, ensure Railway is running

### Issue: Database connection error
**Solution**: Verify `DATABASE_URL` in Railway environment, ensure PostgreSQL service is active

---

## Monitoring & Maintenance

### Railway Dashboard
- Monitor logs: Settings → Logs
- Check resource usage: Metrics tab
- Scale if needed: Pricing tab

### Vercel Dashboard
- Monitor build logs: Deployments tab
- Check Analytics: Analytics tab
- View errors: Functions → Logs tab

---

## Rollback Process

If deployment fails:
1. **Railway**: Previous deployment automatically kept, easy rollback
2. **Vercel**: Previous builds in Deployments tab, click "Redeploy"

---

## Next Steps After Deployment

1. **Enable analytics** to track user behavior
2. **Set up monitoring** for errors and performance
3. **Configure backups** for PostgreSQL on Railway
4. **Set up CI/CD** for automated testing before deploy
5. **Add SSL certificate** (Railway/Vercel handle this automatically)

---

## Support Links

- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment
- Next.js Deployment: https://nextjs.org/docs/deployment

---

**Last Updated**: 2026-06-08
**Status**: Ready for Production Deployment
