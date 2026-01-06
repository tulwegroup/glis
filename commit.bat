@echo off
cd /d c:\Users\gh\glis\ghana_legal_scraper
git init
git config user.name "GLIS Admin"
git config user.email "admin@glis.local"
git add .
git commit -m "Initial GLIS v2.0 - Complete Ghana Legal Intelligence System"
git branch -M main
git remote remove origin >nul 2>&1
git remote add origin https://github.com/tulwegroup/glis.git
git push -u origin main
echo Done!
