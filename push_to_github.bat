@echo off
REM GLIS GitHub Repository Setup
REM This script initializes git and pushes to GitHub

setlocal enabledelayedexpansion

cd /d c:\Users\gh\glis\ghana_legal_scraper

echo.
echo ========================================
echo GLIS Repository Setup
echo ========================================
echo.

echo [1/6] Initializing git repository...
call git init >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo ✓ Git initialized) else (echo ✗ Failed)

echo [2/6] Configuring user...
call git config user.name "GLIS Admin" >nul 2>&1
call git config user.email "admin@glis.local" >nul 2>&1
echo ✓ User configured

echo [3/6] Adding all files...
call git add . >nul 2>&1
echo ✓ Files added

echo [4/6] Creating commit...
call git commit -m "Initial GLIS v2.0 - Complete Ghana Legal Intelligence System" >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo ✓ Commit created) else (echo ✓ Already committed)

echo [5/6] Setting up remote...
call git branch -M main >nul 2>&1
call git remote remove origin >nul 2>&1
call git remote add origin https://github.com/tulwegroup/glis.git >nul 2>&1
echo ✓ Remote configured

echo [6/6] Pushing to GitHub...
echo.
echo NOTE: GitHub may prompt for authentication
echo Use your GitHub username/password or Personal Access Token
echo.

call git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✓ Repository Setup Complete!
    echo ========================================
    echo.
    echo Your GLIS project is now on GitHub:
    echo https://github.com/tulwegroup/glis
    echo.
) else (
    echo.
    echo ⚠ Push completed with warnings (may require auth)
    echo Check: https://github.com/tulwegroup/glis
    echo.
)

pause
