#!/usr/bin/env python3
import subprocess
import os

os.chdir(r"c:\Users\gh\glis\ghana_legal_scraper")

with open(r"c:\Users\gh\glis\ghana_legal_scraper\git_push_log.txt", "w") as log:
    try:
        # Stage all
        r1 = subprocess.run(["git", "add", "."], capture_output=True, text=True, timeout=10)
        log.write(f"ADD: {r1.returncode}\n")
        
        # Commit
        r2 = subprocess.run([
            "git", "commit", "-m", 
            "Deploy GLIS v4.0: Railway backend + Vercel frontend + vector store"
        ], capture_output=True, text=True, timeout=30)
        log.write(f"COMMIT: {r2.returncode}\n{r2.stdout}\n{r2.stderr}\n")
        
        # Push
        r3 = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=30)
        log.write(f"PUSH: {r3.returncode}\n{r3.stdout}\n{r3.stderr}\n")
        
        # Get latest commit info
        r4 = subprocess.run(["git", "log", "-1", "--format=%H|%s|%ai"], capture_output=True, text=True, timeout=10)
        log.write(f"\nLATEST COMMIT:\n{r4.stdout}\n")
        
        log.write("\n✓ GIT OPERATIONS COMPLETE")
        
    except Exception as e:
        log.write(f"ERROR: {e}\n")
