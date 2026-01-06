# GLIS v2.0 - Vercel Deployment Guide

Deploy your interactive GLIS dashboard to Vercel in 5 minutes. **It's free, fast, and requires no setup!**

---

## Why Vercel?

✅ **Free hosting** - No credit card needed
✅ **Instant deploys** - Just push to GitHub  
✅ **Global CDN** - Fast worldwide access
✅ **Automatic scaling** - Handles traffic spikes
✅ **SSL/TLS** - Secure HTTPS by default
✅ **Custom domains** - Add your own domain
✅ **Environment variables** - Secure API keys

---

## Prerequisites

You need:
1. GitHub account (free from github.com)
2. Vercel account (free from vercel.com)
3. This GLIS project pushed to GitHub

---

## Step 1: Prepare Your Local Project

Make sure you have these files in your root directory:

```bash
c:\Users\gh\glis\ghana_legal_scraper\
├── package.json          ← Required
├── next.config.ts        ← Required
├── vercel.json           ← Required
├── app/
│   ├── page.tsx          ← Your dashboard
│   ├── layout.tsx        ← Required
│   └── globals.css       ← Required
├── .gitignore
├── requirements.txt
└── [other files]
```

### Install Dependencies Locally (Optional, for testing)

```powershell
cd c:\Users\gh\glis\ghana_legal_scraper
npm install
npm run dev
```

Visit `http://localhost:3000` to see your dashboard locally.

---

## Step 2: Create GitHub Repository

### Option A: Command Line (Recommended)

```powershell
cd c:\Users\gh\glis\ghana_legal_scraper

# Initialize git
git init
git add .
git commit -m "Initial GLIS dashboard commit"

# Create a repo on GitHub first, then:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/glis-dashboard.git
git push -u origin main
```

### Option B: GitHub Desktop
1. Go to github.com and create a new repository named `glis-dashboard`
2. Open GitHub Desktop
3. File → Add Local Repository
4. Select your `ghana_legal_scraper` folder
5. Publish to GitHub

---

## Step 3: Deploy on Vercel

### Method 1: One-Click Deploy (Easiest)

1. Go to: **https://vercel.com/new**
2. Click "Import Git Repository"
3. Paste your GitHub repo URL: `https://github.com/YOUR_USERNAME/glis-dashboard`
4. Click "Import"
5. Configure project:
   - **Project Name**: `glis-dashboard`
   - **Framework**: `Next.js` (auto-detected)
   - **Root Directory**: `./` (leave as is)
6. Click "Deploy"
7. Wait 2-3 minutes... Done! ✅

### Method 2: From Vercel Dashboard

1. Sign up at https://vercel.com (free)
2. Click "Add New..." → "Project"
3. Select your GitHub repository
4. Click "Import"
5. Click "Deploy"

---

## Step 4: Configure Environment Variables (Optional)

If your backend API is deployed (not local), add the API URL:

1. In Vercel Dashboard, go to **Settings** → **Environment Variables**
2. Add a new variable:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your deployed backend URL (e.g., `https://api.example.com`)
   - **Environments**: Production
3. Click "Save"
4. Redeploy: Click "Deployments" → "..." → "Redeploy"

---

## Step 5: Access Your Dashboard

After deployment completes:

- **Vercel URL**: `https://glis-dashboard-[random].vercel.app`
- You'll see this in the Vercel Dashboard
- Share this URL with your team!

---

## Updating Your Dashboard

Once deployed, updates are **automatic**:

```powershell
# Make changes locally
git add .
git commit -m "Update dashboard"
git push origin main
```

Vercel automatically detects the push and redeploys in ~30 seconds!

---

## Connect Frontend to Backend

### For Local Backend

```javascript
// app/page.tsx already uses:
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

This works if:
- Your local Python API is running on `localhost:8000`
- Running from `http://localhost:3000`

**Note**: Frontend on Vercel + local backend won't work (CORS issues). See below.

### For Deployed Backend

If you deploy your Python backend (Flask/FastAPI), add the URL:

**In Vercel Dashboard:**
1. Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL=https://your-backend.example.com`
3. Redeploy

---

## Deploying Your Python Backend

The dashboard frontend is on Vercel. To use AI features, deploy your Python backend:

### Option 1: Railway (Recommended for Python)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

Get your API URL and add to Vercel environment variables.

### Option 2: Render

1. Go to render.com
2. Create new Web Service
3. Connect your GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn api.main:app --host 0.0.0.0`
6. Deploy

### Option 3: Heroku

```bash
# Install Heroku CLI
npm install -g heroku

heroku login
heroku create your-app-name
git push heroku main
```

---

## Custom Domain (Optional)

Want `glis.example.com` instead of `vercel.app`?

1. Buy domain (godaddy.com, namecheap.com, etc.)
2. In Vercel Dashboard → Settings → Domains
3. Click "Add Domain"
4. Enter your domain name
5. Follow DNS setup instructions
6. Wait 24 hours for DNS propagation

---

## Troubleshooting

### Dashboard shows but API endpoint is offline
- Ensure Python backend is running: `python -m uvicorn api.main:app --reload`
- Check API URL in environment variables
- If deployed, add API URL to Vercel env vars

### Blank page on Vercel
- Check build logs: Vercel Dashboard → Deployments → Click failed deployment
- Ensure `package.json`, `next.config.ts`, and `app/` folder exist
- Run locally: `npm run build && npm start`

### Git push not triggering deploy
- Ensure GitHub is connected in Vercel
- Check branch is `main` (not `master`)
- Redeploy manually: Vercel Dashboard → Deployments → "Redeploy"

### Can't find `requirements.txt`
- Python dependencies are only needed for backend
- Frontend (Vercel) only needs Node.js dependencies from `package.json`

---

## Testing Your Deployment

After deployment, test these:

1. **Dashboard loads**: Visit your Vercel URL
2. **Styling works**: Check colors, layout, fonts
3. **Buttons work**: Click "Deploy on Vercel" button
4. **API status**: Shows "offline" until backend is running (normal)
5. **Responsive**: Test on mobile (should be mobile-friendly)

---

## Next Steps

1. ✅ Deploy to Vercel (you just did this!)
2. 📱 Share dashboard URL with team
3. 🔌 Deploy Python backend separately
4. 🌐 Add custom domain (optional)
5. 🔐 Configure API keys in environment variables
6. 🚀 Start collecting legal data!

---

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs
- **GitHub Help**: https://docs.github.com

---

## Quick Reference

| Task | Command |
|------|---------|
| Test locally | `npm run dev` |
| Build locally | `npm run build` |
| Deploy to Vercel | Push to GitHub (automatic) |
| View logs | Vercel Dashboard → Deployments |
| Update domain | Vercel Dashboard → Settings → Domains |
| Redeploy | Vercel Dashboard → Deployments → Redeploy |

---

**Congrats! Your GLIS dashboard is now live on Vercel!** 🎉
