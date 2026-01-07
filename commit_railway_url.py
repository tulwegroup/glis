#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir(r"c:\Users\gh\glis\ghana_legal_scraper")

try:
    print("📦 Staging environment configuration...")
    subprocess.run(["git", "add", ".env.local"], check=True, capture_output=True)
    
    print("💾 Committing Railway backend URL...")
    result = subprocess.run([
        "git", "commit", "-m", 
        "config: Update backend URL to Railway production (glis-production.up.railway.app)"
    ], check=True, capture_output=True, text=True)
    print(result.stdout)
    
    print("🚀 Pushing to GitHub (Vercel will redeploy)...")
    result = subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
    print(result.stdout)
    print("\n✅ Frontend will redeploy to Vercel with new backend URL!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
