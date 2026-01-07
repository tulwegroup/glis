#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir(r"c:\Users\gh\glis\ghana_legal_scraper")

try:
    # Stage all changes
    print("📦 Staging changes...")
    subprocess.run(["git", "add", "."], check=True, capture_output=True)
    
    # Commit
    print("💾 Committing v4.0 implementation...")
    result = subprocess.run([
        "git", "commit", "-m", 
        "feat: Implement GLIS v4.0 - Complete semantic search, vector store, customary law integration, and Railway deployment config"
    ], check=True, capture_output=True, text=True)
    print(result.stdout)
    
    # Push to GitHub
    print("🚀 Pushing to GitHub...")
    result = subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
    print(result.stdout)
    print("✅ All v4.0 code successfully committed and pushed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
