# Deployment Quick Start

## 🚀 Fast Track to Live Dashboard

### 1. Create GitHub Repo (5 min)
```powershell
cd c:\Users\gh\glis\ghana_legal_scraper
git init
git add .
git commit -m "Initial GLIS dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/glis-dashboard
git push -u origin main
```

### 2. Deploy on Vercel (2 min)
- Go to https://vercel.com/new
- Click "Import Git Repository"
- Paste your GitHub repo URL
- Click "Import" → "Deploy"
- **Done!** Your dashboard is live! ✅

### 3. Get Your Live URL
- Check Vercel Dashboard
- Your URL: `https://glis-dashboard-xxx.vercel.app`
- Share with team!

---

## What You Get

✅ **Free hosting** on Vercel CDN  
✅ **Automatic updates** when you push to GitHub  
✅ **HTTPS/SSL** by default  
✅ **Global speed** with edge caching  
✅ **Custom domains** available  
✅ **Mobile responsive** dashboard  
✅ **Real-time** system status display  

---

## After Deployment

1. **Test your dashboard**: Click the Vercel URL
2. **Connect API**: Add backend URL to environment variables
3. **Start Python backend**: `python -m uvicorn api.main:app --reload`
4. **Test endpoints**: Use Swagger UI at http://localhost:8000/docs

---

For full instructions, see: [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)
