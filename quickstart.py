#!/usr/bin/env python3
"""
Quick Start Guide for Ghana Legal Scraper
Run this script to validate your installation
"""

import sys
import subprocess
from pathlib import Path

print("=" * 70)
print("GHANA LEGAL SCRAPER - QUICK START VALIDATION")
print("=" * 70)
print()

# Check Python version
print("1. Checking Python version...")
version = sys.version_info
if version.major >= 3 and version.minor >= 10:
    print(f"   ✓ Python {version.major}.{version.minor} (OK)")
else:
    print(f"   ✗ Python {version.major}.{version.minor} (requires 3.10+)")
    sys.exit(1)

print()
print("2. Checking directory structure...")
required_dirs = [
    'scraper', 'api', 'config', 'tests', 'utils', 'data', 'data/logs'
]
for d in required_dirs:
    if Path(d).exists():
        print(f"   ✓ {d}/")
    else:
        print(f"   ✗ {d}/ MISSING")

print()
print("3. Checking key files...")
required_files = [
    'main.py', 'requirements.txt', 'README.md',
    'scraper/crawler.py', 'scraper/validator.py', 'scraper/parser.py',
    'api/main.py', 'api/models.py', 'api/search.py',
    'config/settings.py', 'tests/test_scraper.py'
]
for f in required_files:
    if Path(f).exists():
        print(f"   ✓ {f}")
    else:
        print(f"   ✗ {f} MISSING")

print()
print("4. Checking Python dependencies...")
try:
    import fastapi
    import pydantic
    import requests
    import bs4
    print("   ✓ FastAPI")
    print("   ✓ Pydantic")
    print("   ✓ Requests")
    print("   ✓ BeautifulSoup4")
    print("   All required packages found!")
except ImportError as e:
    print(f"   ✗ Missing package: {e}")
    print()
    print("   To install dependencies:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

print()
print("=" * 70)
print("VALIDATION COMPLETE - Ready to use!")
print("=" * 70)
print()
print("Quick start commands:")
print()
print("  1. Run tests (recommended first):")
print("     python main.py test")
print()
print("  2. Start API server:")
print("     python main.py api")
print("     Then visit: http://localhost:8000/docs")
print()
print("  3. Run scraping (test mode - 10 cases):")
print("     python main.py scrape --test")
print()
print("  4. Full scraping campaign:")
print("     python main.py scrape")
print()
print("For detailed documentation, see README.md")
print()
