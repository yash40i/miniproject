# Quick Deployment Guide - Vercel + Railway

## 🚀 TL;DR - Deploy in 15 Minutes

### Prerequisites
- GitHub account with code pushed
- Railway account (free tier available)
- Vercel account (free tier available)
- Production Google OAuth credentials

### Backend Deployment (Railway)

```bash
# 1. Push code to GitHub
git push origin main

# 2. Go to https://railway.app
# 3. Click "New Project" → "GitHub Repo"
# 4. Select your repository
# 5. Railway auto-detects Python app

# 6. Add PostgreSQL service
# - In Railway dashboard, "New Service" → "PostgreSQL"
# - Copy DATABASE_URL connection string

# 7. Set Environment Variables in Railway
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
CORS_ORIGINS=https://your-domain.com
ENVIRONMENT=production
DEBUG=false

# 8. Railway automatically deploys
# - Backend URL: https://your-project.up.railway.app
```

### Frontend Deployment (Vercel)

```bash
# 1. Go to https://vercel.com
# 2. Click "New Project" → "Import Git Repository"
# 3. Select your repository
# 4. Vercel auto-detects Next.js

# 5. Set Build Settings (auto-detected)
# - Framework: Next.js
# - Build Command: npm run build (in frontend dir)
# - Output: .next

# 6. Set Environment Variables
NEXT_PUBLIC_API_URL=https://your-railway-backend-url.up.railway.app
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-production-google-client-id

# 7. Click "Deploy"
# - Vercel automatically builds and deploys
# - Provides URL: https://your-project.vercel.app
```

### Connect Custom Domain

```bash
# Vercel Dashboard → Project Settings → Domains
# 1. Add your domain
# 2. Update DNS CNAME record (Vercel shows exact record)
# 3. Wait for DNS propagation (usually < 1 hour)
# 4. Vercel auto-provisions SSL certificate
```

### Update Google OAuth

```bash
# 1. Google Cloud Console → OAuth consent screen
# 2. Add production domain to "Authorized JavaScript origins"
# 3. Add production domain/callback to "Authorized redirect URIs"
# 4. Update credentials in Railway and Vercel
# 5. Redeploy frontend (Vercel) if env vars changed
```

---

## 📋 Environment Variable Reference

### Railway (.env.production)
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=generated-secret-key-32-chars-minimum
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
CORS_ORIGINS=https://your-domain.com
ENVIRONMENT=production
DEBUG=false
```

### Vercel (frontend/.env.production)
```
NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
NEXT_PUBLIC_GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
```

---

## 🔍 Verify Deployment

```bash
# 1. Test Backend
curl https://your-railway-backend.up.railway.app/docs
# Should see FastAPI Swagger UI

# 2. Test Frontend
# Visit https://your-domain.com
# Should see login/signup pages

# 3. Test Authentication
# - Sign up with email
# - Sign in with Google
# - Check localStorage for auth_token
# - Verify dashboard loads

# 4. Check Logs
# Railway: Dashboard → your-project → Logs
# Vercel: Dashboard → your-project → Deployments → Logs
```

---

## 🛠️ Troubleshooting

### "CORS error"
→ Check `CORS_ORIGINS` in Railway matches your domain

### "Cannot reach backend"
→ Check `NEXT_PUBLIC_API_URL` in Vercel matches Railway URL

### "Database connection failed"
→ Verify `DATABASE_URL` in Railway
→ Ensure PostgreSQL service is running

### "Google sign-in fails"
→ Check Google OAuth credentials match production
→ Verify domain in Google Cloud Console authorized origins

### "Build failed on Railway"
→ Check requirements.txt exists
→ Verify Python 3.10+
→ Check logs: Railway → Logs tab

### "Build failed on Vercel"
→ Check vercel.json exists
→ Verify Build Command is correct
→ Check Node.js version compatibility

---

## 📊 Monitoring After Deploy

### Railway Logs
```bash
Railway Dashboard → Project → Logs
# Watch for errors, connection issues, crashes
```

### Vercel Analytics
```bash
Vercel Dashboard → Project → Analytics
# Monitor page load times, errors, uptime
```

### Database Health
```bash
# In Railway PostgreSQL shell:
SELECT COUNT(*) FROM "user";
# Verify users are being created
```

---

## ♻️ Redeploy When Needed

### For Backend Changes
```bash
# 1. Commit changes to GitHub
git add .
git commit -m "Your message"
git push origin main

# 2. Railway auto-redeploys
# Watch Logs tab for deployment progress
```

### For Frontend Changes
```bash
# 1. Commit changes to GitHub
git add .
git commit -m "Your message"
git push origin main

# 2. Vercel auto-redeploys
# Watch Deployments tab for progress
```

### For Environment Variable Changes
```bash
# 1. Update in Railway/Vercel dashboard
# 2. Manually trigger redeploy
# 3. Monitor logs for new deployment
```

---

## 🔐 Security Reminders

- ✅ Never commit `.env.production` to git
- ✅ Use strong SECRET_KEY (32+ random characters)
- ✅ Rotate GOOGLE_CLIENT_SECRET periodically
- ✅ Enable 2FA on Railway and Vercel accounts
- ✅ Keep PostgreSQL backups
- ✅ Monitor logs for suspicious activity

---

## 📞 Support Resources

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- FastAPI Production: https://fastapi.tiangolo.com/deployment
- Next.js Production: https://nextjs.org/docs/deployment

---

**Ready to Deploy? Start here:**
1. Commit code → 2. Deploy Railway → 3. Deploy Vercel → 4. Add Domain → 5. Update Google OAuth → 6. Test Everything

**Estimated Time**: 15-30 minutes
**Cost**: Free tier available for both Railway and Vercel (with usage limits)
