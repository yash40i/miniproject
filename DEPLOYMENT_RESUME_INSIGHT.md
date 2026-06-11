# Deployment Step-by-Step Guide - resume-insight.com

**Your Setup**:
- Domain: `resume-insight.com`
- Frontend: Vercel
- Backend: Railway
- Database: PostgreSQL (Railway)
- Google OAuth Client ID: `943431102226-k16ljeq9p3gn6p6kqrck6vd9dgkpae1p.apps.googleusercontent.com`

---

## 🔴 STEP 1: Create Railway Account (5 minutes)

### 1.1: Sign Up for Railway
1. Go to https://railway.app
2. Click "Sign up with GitHub" (recommended)
3. Authorize Railway to access your GitHub account
4. Complete the onboarding

### 1.2: Create New Project
1. In Railway dashboard, click "Create Project"
2. Select "Deploy from GitHub repo"
3. Search for your `res_project` repository
4. Select it and click "Deploy"

**Railway will now start building your backend!**

---

## 🟢 STEP 2: Add PostgreSQL Database (2 minutes)

### 2.1: Add Database Service
1. In your Railway project dashboard
2. Click "New Service" → "Database" → "PostgreSQL"
3. Railway automatically creates and starts PostgreSQL

### 2.2: Get Database Connection String
1. Click on the PostgreSQL service
2. Go to "Connect" tab
3. Under "Connection string", you'll see:
   ```
   postgresql://username:password@host:port/railway
   ```
4. **Copy this entire connection string** - you'll need it in a moment

---

## 🔵 STEP 3: Configure Backend Environment Variables (3 minutes)

### 3.1: Generate Secret Key
Open PowerShell and run:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output (your SECRET_KEY)

### 3.2: Set Variables in Railway
1. In Railway dashboard, click "Variables" tab
2. Add these environment variables:

```
DATABASE_URL = [paste from Step 2.2 above]
SECRET_KEY = [paste from Step 3.1 above]
GOOGLE_CLIENT_ID = 943431102226-k16ljeq9p3gn6p6kqrck6vd9dgkpae1p.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET = [your production Google Client Secret]
CORS_ORIGINS = https://resume-insight.com,https://www.resume-insight.com
ENVIRONMENT = production
DEBUG = false
```

3. Click "Save" for each variable

**Railway will automatically restart your backend with these new variables!**

### 3.3: Get Your Backend URL
1. In Railway dashboard, click on your web service
2. Go to "Deployments" tab
3. Look for the URL (something like `https://res-project-prod.up.railway.app`)
4. **Copy this URL** - you'll need it for Vercel in Step 5

### 3.4: Verify Backend Deployed
1. Visit `https://your-railway-url/docs` (replace with actual URL)
2. You should see FastAPI Swagger UI
3. ✅ If you see it, backend is deployed successfully!

---

## 🌐 STEP 4: Create Vercel Account & Deploy Frontend (5 minutes)

### 4.1: Sign Up for Vercel
1. Go to https://vercel.com
2. Click "Sign up" → "Continue with GitHub"
3. Authorize Vercel to access your GitHub account
4. Complete the onboarding

### 4.2: Deploy Frontend
1. In Vercel dashboard, click "New Project"
2. Under "Import Git Repository", search for `res_project`
3. Click "Import"
4. Keep default settings (Vercel auto-detects Next.js)
5. Click "Deploy"

**Vercel will now build and deploy your frontend!**

### 4.3: Add Environment Variables
1. After deployment starts, go to "Settings" → "Environment Variables"
2. Add these two variables:

```
NEXT_PUBLIC_API_URL = https://your-railway-url (from Step 3.3)
NEXT_PUBLIC_GOOGLE_CLIENT_ID = 943431102226-k16ljeq9p3gn6p6kqrck6vd9dgkpae1p.apps.googleusercontent.com
```

3. Click "Save"
4. **Important**: Go back to "Deployments" and click "Redeploy" on the latest build

### 4.4: Get Your Vercel URL
1. After redeployment completes, click on the deployment
2. You'll see a URL like `https://res-project.vercel.app`
3. **Copy this URL** - this is your temporary frontend URL

### 4.5: Test Frontend Deployed
1. Visit your Vercel URL (e.g., `https://res-project.vercel.app`)
2. You should see your login page
3. ✅ If you see it, frontend is deployed successfully!

---

## 🔗 STEP 5: Connect Custom Domain to Vercel (5 minutes)

### 5.1: Add Domain in Vercel
1. In Vercel project, go to "Settings" → "Domains"
2. In "Production Domains", type: `resume-insight.com`
3. Click "Add"

### 5.2: Configure DNS Records
Vercel will show you DNS records to add. Follow these steps **at your domain registrar**:

**Example registrars**: GoDaddy, Namecheap, Google Domains, Cloudflare

1. Log into your domain registrar
2. Go to DNS settings for `resume-insight.com`
3. Add the CNAME record Vercel provides (usually looks like):
   ```
   Host: www
   Value: cname.vercel-dns.com
   ```
4. Also add an A record pointing to Vercel's IP
5. Save changes

### 5.3: Wait for DNS Propagation
- DNS changes take 5-48 hours to propagate (usually < 1 hour)
- You can check status at: https://www.whatsmydns.net/
- Vercel will show "Valid Configuration" when it's ready

### 5.4: Verify Domain Works
Once DNS is propagated:
1. Visit `https://resume-insight.com`
2. You should see your login page
3. ✅ Congratulations! Frontend is live!

---

## 🔐 STEP 6: Configure Google OAuth for Production (3 minutes)

### 6.1: Update Google Cloud Console
1. Go to https://console.cloud.google.com
2. Go to your project → APIs & Services → Credentials
3. Click on your OAuth 2.0 Client ID
4. Under "Authorized JavaScript origins", add:
   - `https://resume-insight.com`
   - `https://www.resume-insight.com`
5. Under "Authorized redirect URIs", add:
   - `https://resume-insight.com/api/auth/callback`
   - `https://www.resume-insight.com/api/auth/callback`
6. Click "Save"

### 6.2: Update Environment Variables (if needed)
- If you changed Google Client Secret, update it in Railway and Vercel
- Vercel will auto-redeploy if you change env vars
- Railway will auto-redeploy

---

## ✅ STEP 7: Test Production Deployment (10 minutes)

### 7.1: Test Authentication Flow
1. Visit `https://resume-insight.com`
2. Try the signup form:
   - Enter email, password, name
   - Click "Create Account"
   - Should redirect to dashboard
   - Check localStorage has `auth_token`

3. Try logout:
   - Click user menu
   - Click "Logout"
   - Should redirect to login
   - Token should be cleared from localStorage

4. Try login:
   - Enter same email/password
   - Click "Sign In"
   - Should redirect to dashboard

### 7.2: Test Google OAuth
1. Visit `https://resume-insight.com/signup`
2. Click "Sign in with Google" button
3. Complete Google authentication
4. Should redirect to dashboard
5. Should see user info in menu
6. Check localStorage for `auth_token`

### 7.3: Check Backend Logs
1. Go to Railway dashboard
2. Click on your project
3. Click "Logs" tab
4. You should see:
   - POST requests to `/auth/signup`
   - POST requests to `/auth/login`
   - POST requests to `/auth/google`
   - No errors (look for red text)

### 7.4: Check Database
1. In Railway, click PostgreSQL service
2. Click "Connect" tab
3. Click "Query Editor"
4. Run:
   ```sql
   SELECT email, oauth_provider FROM "user" LIMIT 5;
   ```
5. You should see your test users

### 7.5: Monitor Vercel
1. Go to Vercel dashboard
2. Click "Analytics" tab
3. You should see page views and performance metrics
4. Click "Deployments" → latest build
5. Check "Logs" for any errors

---

## 🎉 DEPLOYMENT COMPLETE!

**Your app is now live at**: `https://resume-insight.com`

### What You Have
✅ Frontend deployed on Vercel (Global CDN, auto-scaling)
✅ Backend deployed on Railway (Auto-restarting, easy scaling)
✅ Database on PostgreSQL (Secure, auto-backed up)
✅ Custom domain connected
✅ SSL/HTTPS enabled automatically
✅ Google OAuth working
✅ Email/password authentication working

---

## 📊 Monitoring Your Production App

### Daily Checks
1. **Vercel Dashboard**
   - Check deployments for failures
   - Monitor error rates in Analytics
   - Watch function execution times

2. **Railway Dashboard**
   - Check backend logs for errors
   - Monitor CPU and memory usage
   - Verify database is connected

3. **App Functionality**
   - Test signup/login daily
   - Try Google OAuth
   - Check for error messages

### Weekly Checks
1. Check PostgreSQL database size
2. Review user count: `SELECT COUNT(*) FROM "user";`
3. Review error logs for patterns
4. Check performance metrics

---

## 🚨 Troubleshooting

### "Cannot connect to backend"
- Check `NEXT_PUBLIC_API_URL` in Vercel matches Railway URL
- Check Railway backend is running (check Deployments)
- Check CORS_ORIGINS in Railway includes your domain

### "Google login fails"
- Check domain is in Google Cloud authorized origins
- Check OAuth credentials haven't changed
- Verify Client Secret is correct in Railway

### "Database connection error"
- Check `DATABASE_URL` in Railway is correct
- Verify PostgreSQL service is running
- Check database credentials match

### "Deployment fails"
- Railway: Check Logs tab for build errors
- Vercel: Check Deployments tab for build errors
- Verify all environment variables are set

---

## 🔄 Redeployment (for code changes)

Your apps auto-deploy when you push to GitHub!

```bash
# Make changes locally
git add .
git commit -m "Your message"
git push origin main

# Railway auto-redeploys backend
# Vercel auto-redeploys frontend
# Watch their dashboards for deployment progress
```

---

## 📈 Next Steps

After deployment:
1. **Gather Feedback** - Have users test the auth flow
2. **Monitor Performance** - Watch for slow requests
3. **Optimize** - Add caching, optimize queries if needed
4. **Scale** - Upgrade Railway/Vercel if traffic grows
5. **Iterate** - Add new features based on feedback

---

## 💡 Quick Reference URLs

- **Production App**: https://resume-insight.com
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Railway Dashboard**: https://railway.app
- **Google Cloud Console**: https://console.cloud.google.com
- **DNS Checker**: https://www.whatsmydns.net/

---

## ✨ Congratulations!

Your Resume-Insight AI authentication system is now **live in production**! 

Users can:
- ✅ Sign up with email
- ✅ Log in with email
- ✅ Authenticate with Google
- ✅ Access protected dashboard
- ✅ Have their data persisted in PostgreSQL

---

**Last Updated**: 2026-06-08
**Status**: DEPLOYMENT GUIDE - READY TO EXECUTE
