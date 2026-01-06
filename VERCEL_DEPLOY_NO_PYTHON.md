# 🚀 Deploy GLIS to Vercel - Complete Guide (No Python Needed!)

Since you can't install Python locally, here's the **smartest approach:**

✓ Deploy **Next.js frontend** to Vercel (free, takes 5 minutes)  
✓ Deploy **Python backend** separately (optional, can do later)  
✓ Connect them together  

---

## Phase 1: Push Code to GitHub

You need git to be installed (it usually is on Windows). Let's push your code:

### Option A: Use Git Command Line (Simplest)

Open **Command Prompt** (not PowerShell) and run:

```cmd
cd c:\Users\gh\glis\ghana_legal_scraper
git init
git config user.name "GLIS Admin"
git config user.email "admin@glis.local"
git add .
git commit -m "Initial GLIS v2.0"
git branch -M main
git remote add origin https://github.com/tulwegroup/glis.git
git push -u origin main
```

When it asks for authentication:
- Use your GitHub username
- Use your GitHub password (or Personal Access Token if you have 2FA)

**That's it!** ✓

### Option B: Use Node.js Script

If Command Prompt doesn't work, try Node.js (usually included):

```powershell
cd c:\Users\gh\glis\ghana_legal_scraper
node push-to-github.js
```

### Option C: Use GitHub Desktop

1. Download: https://desktop.github.com
2. Open GitHub Desktop
3. File → Add Local Repository
4. Select: `c:\Users\gh\glis\ghana_legal_scraper`
5. Publish to GitHub

---

## Phase 2: Deploy Frontend to Vercel

Once code is on GitHub:

### Step 1: Go to Vercel
👉 **https://vercel.com/new**

### Step 2: Click "Import Git Repository"

### Step 3: Authorize GitHub
- Click "Authorize with GitHub"
- Select your account
- Click "Install & Authorize"

### Step 3: Select Your Repository
- Find **`tulwegroup/glis`**
- Click "Import"

### Step 4: Configure Project
Leave defaults:
- Project Name: `glis-dashboard`
- Framework: Next.js (auto-detected)
- Root Directory: `./`
- Click **"Deploy"**

### Step 5: Wait & Get URL
In 2-3 minutes, Vercel gives you a live URL like:
```
https://glis-dashboard-xxx.vercel.app
```

**✓ Your dashboard is now LIVE!** 🎉

---

## Phase 3: (Optional) Deploy Python Backend

Once frontend is deployed, you can optionally deploy the Python backend:

### Option A: Railway (Recommended for Python)

1. Go to: https://railway.app
2. Click "New Project"
3. Select "GitHub Repo"
4. Choose `tulwegroup/glis`
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
6. Deploy!
7. Get your API URL from Railway dashboard
8. Add to Vercel environment variables:
   - `NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app`

### Option B: Render

1. Go to: https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Configure same as above
5. Deploy!

---

## What You Have Now

✓ **Next.js Dashboard** - Deployed on Vercel  
✓ **Interactive UI** - Shows all 13 endpoints, system status  
✓ **Real-time API Status** - Shows if backend is online  
✓ **Global CDN** - Fast worldwide access  
✓ **Free Hosting** - Zero cost forever  
✓ **Auto Updates** - Push to GitHub = auto deploy  

---

## After Deployment

### Your URLs:
- **Frontend:** `https://glis-dashboard-xxx.vercel.app`
- **Backend** (optional): `https://your-api.railway.app` or similar

### Test Your Dashboard:
1. Visit your Vercel URL
2. See all system stats
3. View all 13 API endpoints
4. Get setup instructions
5. API status shows "offline" until backend is running (normal)

### If You Deploy Backend:
1. Add API URL to Vercel environment variables
2. Redeploy
3. Dashboard auto-detects and shows "online" ✓

---

## FAQ

**Q: Do I need Python to deploy the frontend?**  
A: No! It's a Next.js app, uses Node.js. Python is only for the backend.

**Q: What if I don't deploy the Python backend?**  
A: The dashboard still works! You can view:
- System documentation
- API endpoint reference
- Setup instructions
- All status info

Backend features just show "offline" until you deploy it.

**Q: Can I deploy the backend later?**  
A: Yes! Deploy frontend now, backend whenever you're ready.

**Q: How much does this cost?**  
A: **$0** forever. Both Vercel and Railway have free tiers.

**Q: What if I want a custom domain?**  
A: Add it in Vercel Settings → Domains. You need to own the domain.

---

## Quick Summary

```
Your Machine:
- Can't install Python ✗
- But have git & Node.js ✓

Next.js Dashboard:
- Deploys to Vercel ✓
- No Python needed ✓
- Takes 5 minutes ✓
- Completely free ✓

Python Backend:
- Deploy to Railway/Render ✓
- Can do later ✓
- Optional ✓
```

---

## Let's Get Started!

**Right now, do this:**

1. Push to GitHub (use Command Prompt for Option A)
2. Go to https://vercel.com/new
3. Import your GitHub repo
4. Click "Deploy"
5. Wait 3 minutes
6. **Your dashboard is live!** 🚀

**Done!** No Python installation needed! ✨
