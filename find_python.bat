@echo off
REM Find Python installation

echo Searching for Python...
echo.

REM Check common installation locations
if exist C:\Python312\python.exe (
    echo Found Python at: C:\Python312\python.exe
    goto found
)

if exist C:\Python311\python.exe (
    echo Found Python at: C:\Python311\python.exe
    goto found
)

if exist C:\Python310\python.exe (
    echo Found Python at: C:\Python310\python.exe
    goto found
)

if exist "%APPDATA%\..\Local\Programs\Python\Python312\python.exe" (
    echo Found Python at: %APPDATA%\..\Local\Programs\Python\Python312\python.exe
    goto found
)

if exist "%APPDATA%\..\Local\Programs\Python\Python311\python.exe" (
    echo Found Python at: %APPDATA%\..\Local\Programs\Python\Python311\python.exe
    goto found
)

REM Try py.exe (Windows Python launcher)
for /f "tokens=*" %%A in ('where py.exe 2^>nul') do (
    echo Found Python launcher: %%A
    echo.
    echo To run the test, use:
    echo   py -3 quick_test.py
    echo   py -3 run_glis.py
    goto end
)

echo.
echo Python not found in standard locations.
echo.
echo Please install Python from: https://www.python.org/downloads/
echo Or check Settings ^> Manage App Execution Aliases to enable Python
echo.

:found
echo.
echo Python is installed and ready!
echo.
echo To test the system, run:
echo   python quick_test.py
echo   python run_glis.py
echo.

:end
pause
