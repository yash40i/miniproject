# DEPLOYMENT CHECKLIST - Resume-Insight AI

## Pre-Deployment (Local Setup)

- [ ] All code committed to GitHub repository
- [ ] `.env.production` created with production secrets
- [ ] Production secrets are NOT in version control
- [ ] Frontend production build tested locally: `npm run build`
- [ ] Backend tested with production settings

## Step 1: Set Up Database (Railway PostgreSQL)

- [ ] Railway account created (https://railway.app)
- [ ] New PostgreSQL service provisioned
- [ ] DATABASE_URL copied from Railway
- [ ] Test connection string works
- [ ] Database backup configured (if available in plan)

## Step 2: Deploy Backend (Railway)

### Initial Setup
- [ ] GitHub connected to Railway
- [ ] Repository selected and authorized
- [ ] Procfile added to repository root
- [ ] railway.json added to repository root

### Environment Variables in Railway
- [ ] `DATABASE_URL` set to PostgreSQL connection
- [ ] `SECRET_KEY` generated and set (min 32 chars)
- [ ] `GOOGLE_CLIENT_ID` set (production)
- [ ] `GOOGLE_CLIENT_SECRET` set (production)
- [ ] `CORS_ORIGINS` set to production domain
- [ ] `ENVIRONMENT` set to "production"
- [ ] `DEBUG` set to "false"

### Verification
- [ ] Backend deployed successfully (no build errors)
- [ ] Railway provides backend URL (e.g., your-project.up.railway.app)
- [ ] Backend health check responds: `https://backend-url/docs`
- [ ] PostgreSQL service is running
- [ ] Logs show no database connection errors

## Step 3: Deploy Frontend (Vercel)

### Initial Setup
- [ ] Vercel account created (https://vercel.com)
- [ ] GitHub repository connected to Vercel
- [ ] vercel.json added to repository root
- [ ] frontend/.env.production.example created

### Environment Variables in Vercel
- [ ] `NEXT_PUBLIC_API_URL` set to Railway backend URL
- [ ] `NEXT_PUBLIC_GOOGLE_CLIENT_ID` set (production)

### Build Configuration
- [ ] Build command: `cd frontend && npm run build`
- [ ] Output directory: `frontend/.next`
- [ ] Install command: `cd frontend && npm ci`

### Verification
- [ ] Frontend deployed successfully (no build errors)
- [ ] Vercel provides frontend URL (e.g., your-project.vercel.app)
- [ ] Frontend loads without console errors
- [ ] API calls to backend work (check Network tab)

## Step 4: Custom Domain Setup

### DNS Configuration
- [ ] Domain registrar account accessed
- [ ] CNAME record added for Vercel (provided by Vercel)
- [ ] DNS propagation verified (up to 48 hours, usually < 1 hour)
- [ ] SSL certificate auto-provisioned by Vercel

### Domain Verification
- [ ] `https://your-domain.com` loads frontend
- [ ] No SSL certificate warnings
- [ ] All resources load over HTTPS

## Step 5: Google OAuth Configuration

### Google Cloud Console
- [ ] New OAuth 2.0 credential created (Web app type)
- [ ] Authorized JavaScript origins updated:
  - [ ] `https://your-domain.com`
  - [ ] `https://www.your-domain.com`
- [ ] Authorized redirect URIs updated:
  - [ ] `https://your-domain.com/api/auth/callback`
- [ ] Production Client ID copied
- [ ] Production Client Secret copied

### Verification
- [ ] Environment variables updated in both Railway and Vercel
- [ ] Vercel redeployed after env var changes
- [ ] Google sign-in button visible on signup/login
- [ ] Google sign-in flow completes without errors

## Step 6: End-to-End Testing

### Authentication Flow
- [ ] Visit `https://your-domain.com/signup`
- [ ] Email/password signup works
- [ ] Token stored in localStorage
- [ ] Redirected to dashboard
- [ ] User info displayed in account menu
- [ ] Logout clears token and redirects to login
- [ ] Login with same credentials works
- [ ] Google "Sign in" button works
- [ ] Google authentication completes successfully
- [ ] Token properly stored after Google auth

### Protected Routes
- [ ] Clear localStorage (logout)
- [ ] Visit `https://your-domain.com/` (dashboard)
- [ ] Redirected to login page
- [ ] Query parameter `?from=/` preserved
- [ ] After login, redirected back to original page

### API Integration
- [ ] Check Network tab in DevTools
- [ ] API requests sent to correct backend URL
- [ ] Authorization header includes JWT token
- [ ] API responses successful (200 status)
- [ ] Error responses handled gracefully in UI

### Database
- [ ] New user created in PostgreSQL after signup
- [ ] User data persists across logins
- [ ] Google OAuth user metadata stored correctly
- [ ] Query: `SELECT * FROM "user" LIMIT 5;` in Railway

## Step 7: Performance & Monitoring

### Vercel Monitoring
- [ ] Check Vercel Analytics for page load times
- [ ] Monitor function execution times
- [ ] Check for any 4xx/5xx errors
- [ ] Review resource usage

### Railway Monitoring
- [ ] Check CPU usage (should be low)
- [ ] Monitor memory usage
- [ ] View application logs for errors
- [ ] Check database connections

### Browser Console
- [ ] No JavaScript errors in console
- [ ] No CORS errors in Network tab
- [ ] No unhandled promise rejections
- [ ] All API requests successful

## Step 8: Security Checklist

- [ ] Production secrets NOT in git repository
- [ ] `.env.production` in .gitignore
- [ ] SSL/HTTPS enabled everywhere
- [ ] CORS configured to specific origins (not wildcard)
- [ ] JWT SECRET_KEY is strong (32+ characters)
- [ ] Google OAuth secrets kept confidential
- [ ] Database backups configured
- [ ] No sensitive data in URLs or query strings

## Step 9: Backup & Recovery

- [ ] Database backups enabled on Railway
- [ ] Backup retention period set (minimum 7 days)
- [ ] Recovery procedure documented
- [ ] Test restore from backup works

## Step 10: Documentation & Handoff

- [ ] DEPLOYMENT_GUIDE.md complete and accurate
- [ ] Production database connection documented (securely)
- [ ] Admin credentials/access documented
- [ ] Monitoring alerts configured
- [ ] On-call runbook created for troubleshooting

## Post-Deployment

- [ ] Monitor logs for 24-48 hours
- [ ] Watch for error spikes
- [ ] Verify all user flows work smoothly
- [ ] Gather user feedback
- [ ] Plan rollback procedure if needed

## Rollback Plan

If critical issues occur:
1. **Immediate**: Revert Vercel deployment (use previous build)
2. **If DB issue**: Restore from Railway backup
3. **If backend fails**: Deploy previous Railway build
4. **Communication**: Notify users of downtime

## Success Criteria

✅ **All items checked** = Ready for production
✅ **Users can sign up, login, and use Google OAuth**
✅ **No console errors or warnings**
✅ **API responding with < 200ms latency**
✅ **Database persisting data correctly**
✅ **SSL/HTTPS working everywhere**

---

## Quick Rollback Commands

```bash
# Vercel: Use dashboard → Deployments → Rollback
# Railway: Use dashboard → Deployments → Previous build
# Restart backend: Railway dashboard → Redeploy
```

---

**Deployment Date**: _________________
**Deployed By**: _________________
**Production URL**: https://your-domain.com
**Backend URL**: https://your-railway-backend-url.up.railway.app

---

Last Updated: 2026-06-08
