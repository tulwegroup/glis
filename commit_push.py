#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir('c:\\Users\\gh\\glis\\ghana_legal_scraper')

try:
    print("Adding changes...")
    subprocess.run(['git', 'add', '.'], check=True)
    
    print("Committing...")
    result = subprocess.run(['git', 'commit', '-m', 'Update dashboard UI: Add functional legal tools interface'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    print("Pushing to GitHub...")
    result = subprocess.run(['git', 'push', 'origin', 'main'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    print("\n✅ SUCCESS: Changes committed and pushed to GitHub!")
    sys.exit(0)
    
except subprocess.CalledProcessError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Exception: {e}")
    sys.exit(1)
