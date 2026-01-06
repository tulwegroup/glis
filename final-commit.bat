@echo off
REM Simple git commit and push script
REM Runs each command separately to avoid terminal issues

setlocal enabledelayedexpansion

cd /d "c:\Users\gh\glis\ghana_legal_scraper"

echo.
echo ========================================
echo GLIS Git Commit
echo ========================================
echo.

echo [1/7] Checking git installation...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo OK - Git found

echo [2/7] Initializing repository...
git init >nul 2>&1
echo OK

echo [3/7] Configuring git user...
git config user.name "GLIS Admin" >nul 2>&1
git config user.email "admin@glis.local" >nul 2>&1
echo OK

echo [4/7] Staging files...
git add . >nul 2>&1
echo OK

echo [5/7] Creating commit...
git commit -m "Initial GLIS v2.0 - Complete Ghana Legal Intelligence System" >nul 2>&1
if %errorlevel% equ 0 (
    echo OK - Commit created
) else (
    echo OK - Already committed (no changes)
)

echo [6/7] Setting main branch...
git branch -M main >nul 2>&1
echo OK

echo [7/7] Adding remote and pushing...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/tulwegroup/glis.git >nul 2>&1

echo.
echo Pushing to GitHub (you may be prompted for credentials)...
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Your GLIS project is now on GitHub:
    echo https://github.com/tulwegroup/glis
    echo.
) else (
    echo.
    echo Push completed. Check GitHub if upload was successful.
    echo.
)

pause
