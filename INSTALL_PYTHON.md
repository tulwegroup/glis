# Install Python - Complete Guide

## Download Python

**Direct Download Link:**
👉 **https://www.python.org/downloads/windows/**

Or click here for the latest version:
👉 **https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe**

---

## Installation Steps

### Step 1: Download
1. Go to: https://www.python.org/downloads/windows/
2. Click **"Download Python 3.12.1"** (or latest version)
3. Save the `.exe` file

### Step 2: Run Installer
1. Double-click the downloaded `.exe` file
2. **IMPORTANT:** Check the box: **"Add Python 3.12 to PATH"** ☑️
3. Click **"Install Now"** (or "Customize installation")

### Step 3: Wait for Installation
The installer will take 1-2 minutes to complete.

### Step 4: Verify Installation
Open **PowerShell** and run:
```powershell
python --version
```

**Expected output:**
```
Python 3.12.1
```

If you see this, Python is installed! ✓

---

## Quick Installation (Recommended Settings)

**Default options work fine:**
- ✓ Add Python to PATH (MUST CHECK)
- ✓ Install pip (package manager)
- ✓ Install IDLE (code editor)
- ✓ Install venv (virtual environments)

**Don't change anything else** - just click through with default settings.

---

## After Installation

Once Python is installed, you can:

### Option 1: Run the commit script
```powershell
cd c:\Users\gh\glis\ghana_legal_scraper
python commit_to_github.py
```

### Option 2: Or use the batch file (still works)
```powershell
c:\Users\gh\glis\ghana_legal_scraper\push_to_github.bat
```

### Option 3: Or run git directly
```powershell
cd c:\Users\gh\glis\ghana_legal_scraper
git init
git add .
git commit -m "Initial GLIS v2.0"
git branch -M main
git remote add origin https://github.com/tulwegroup/glis.git
git push -u origin main
```

---

## Troubleshooting

### "Python not found" after installation
**Solution:** Restart PowerShell/Command Prompt after installing Python

### "Add Python to PATH" checkbox missing
**Solution:** Uninstall Python, download again, and check that checkbox during installation

### Still getting errors
**Alternative:** Use the batch file `push_to_github.bat` (doesn't need Python)

---

## Need Help?

- **Python Install Help:** https://docs.python.org/3/using/windows.html
- **GitHub Setup Help:** https://docs.github.com/en/get-started

---

## Next Steps After Python Installation

1. ✓ Install Python (you're here)
2. ✓ Verify: `python --version`
3. ✓ Run: `python commit_to_github.py`
4. ✓ Push to GitHub complete!

**It takes 5 minutes total!** ⏱️
