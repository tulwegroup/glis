#!/usr/bin/env python3
"""
Direct git operations to push to GitHub without terminal display issues
"""
import subprocess
import sys
import os

# Change to repo directory
os.chdir(r"c:\Users\gh\glis\ghana_legal_scraper")

try:
    # Get current HEAD
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        timeout=10
    )
    current_commit = result.stdout.strip()
    print(f"Current local commit: {current_commit[:8]}")
    
    # Check for changes to commit
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.stdout.strip():
        print(f"Files to commit:\n{result.stdout}")
        
        # Add all changes
        subprocess.run(["git", "add", "."], check=True, capture_output=True, timeout=10)
        
        # Commit
        subprocess.run([
            "git", "commit",
            "-m", "Deploy GLIS v4.0: Railway backend integration + Vercel frontend"
        ], check=True, capture_output=True, timeout=30)
        
        print("✓ Committed")
    else:
        print("No changes to commit")
    
    # Push to GitHub
    print("\nPushing to GitHub...")
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print("✓ Successfully pushed to GitHub!")
        print(f"Output: {result.stdout[:200] if result.stdout else 'Silent success'}")
    else:
        print(f"Push output: {result.stdout}")
        print(f"Push error: {result.stderr}")
        sys.exit(1)
        
    # Verify push
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H %s"],
        capture_output=True,
        text=True,
        timeout=10
    )
    print(f"\nLatest commit: {result.stdout}")
    
except subprocess.TimeoutExpired:
    print("Command timed out")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
