@echo off
REM GitHub GLIS Repository Setup Script
REM This script initializes git and pushes to GitHub

cd /d c:\Users\gh\glis\ghana_legal_scraper

echo.
echo ========================================
echo GLIS Repository Setup
echo ========================================
echo.

REM Initialize git if not already done
if not exist ".git" (
    echo [1/5] Initializing git repository...
    git init
    git config user.name "GLIS Admin"
    git config user.email "admin@glis.local"
    echo ✓ Git initialized
) else (
    echo [1/5] Git already initialized
)

echo.
echo [2/5] Adding all files...
git add .
echo ✓ Files added

echo.
echo [3/5] Creating initial commit...
git commit -m "Initial GLIS v2.0 - Complete Ghana Legal Intelligence System"
echo ✓ Commit created

echo.
echo [4/5] Setting up remote repository...
REM Remove existing origin if it exists
git remote remove origin >nul 2>&1

REM Add new origin
git remote add origin https://github.com/tulwegroup/glis.git
echo ✓ Remote 'origin' added

echo.
echo [5/5] Pushing to GitHub...
echo.
echo NOTE: You will be prompted to authenticate with GitHub.
echo Use one of these methods:
echo   - Personal Access Token (recommended)
echo   - GitHub SSH key
echo   - GitHub credentials
echo.
echo For help, see: https://docs.github.com/en/get-started/getting-started-with-git/about-remote-repositories
echo.

git branch -M main
git push -u origin main

echo.
echo ========================================
echo ✓ Repository setup complete!
echo ========================================
echo.
echo Your GLIS project is now on GitHub:
echo https://github.com/tulwegroup/glis
echo.
pause
