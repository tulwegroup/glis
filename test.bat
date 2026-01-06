@echo off
REM GLIS Quick Test Script
REM Tests Layer 3 components without needing API server

cd /d c:\Users\gh\glis\ghana_legal_scraper

REM Try to find Python in common locations
set PYTHON=python
if not exist %PYTHON% (
    if exist C:\Python312\python.exe (
        set PYTHON=C:\Python312\python.exe
    ) else if exist C:\Python311\python.exe (
        set PYTHON=C:\Python311\python.exe
    ) else if exist C:\Python310\python.exe (
        set PYTHON=C:\Python310\python.exe
    ) else if exist %APPDATA%\..\Local\Programs\Python\Python312\python.exe (
        set PYTHON=%APPDATA%\..\Local\Programs\Python\Python312\python.exe
    )
)

echo.
echo ===================================
echo GLIS Quick Test
echo ===================================
echo.
echo Python: %PYTHON%
echo Working Directory: %CD%
echo.

REM Run quick test
echo Running quick_test.py...
echo.
%PYTHON% quick_test.py

echo.
echo ===================================
echo Test Complete
echo ===================================
echo.
pause
