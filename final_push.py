#!/usr/bin/env python3
import subprocess
import os

os.chdir(r"c:\Users\gh\glis\ghana_legal_scraper")

# Check current status
print("=== GIT STATUS ===")
result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
print(result.stdout if result.stdout else "No changes")

print("\n=== RECENT COMMITS ===")
result = subprocess.run(["git", "log", "--oneline", "-3"], capture_output=True, text=True)
print(result.stdout)

print("\n=== STAGING CHANGES ===")
result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
print("Staged")

print("\n=== COMMITTING ===")
result = subprocess.run([
    "git", "commit", "-m", 
    "chore: Deploy GLIS v4.0 with Railway backend integration"
], capture_output=True, text=True)
print(result.stdout if result.stdout else result.stderr)

print("\n=== PUSHING ===")
result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
print(result.stdout if result.stdout else result.stderr)
print("DONE" if result.returncode == 0 else f"ERROR: {result.returncode}")
