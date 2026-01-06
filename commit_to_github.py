#!/usr/bin/env python3
"""
GLIS GitHub Repository Setup Script
This script initializes git and pushes to GitHub
"""

import os
import subprocess
import sys

os.chdir(r'c:\Users\gh\glis\ghana_legal_scraper')

commands = [
    ['git', 'init'],
    ['git', 'config', 'user.name', 'GLIS Admin'],
    ['git', 'config', 'user.email', 'admin@glis.local'],
    ['git', 'add', '.'],
    ['git', 'commit', '-m', 'Initial GLIS v2.0 - Complete Ghana Legal Intelligence System'],
    ['git', 'branch', '-M', 'main'],
    ['git', 'remote', 'remove', 'origin'],
    ['git', 'remote', 'add', 'origin', 'https://github.com/tulwegroup/glis.git'],
    ['git', 'push', '-u', 'origin', 'main'],
]

print("=" * 50)
print("GLIS Repository Setup")
print("=" * 50)
print()

for i, cmd in enumerate(commands, 1):
    print(f"[{i}/{len(commands)}] Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Success")
        else:
            if 'nothing to commit' in result.stderr or 'nothing to commit' in result.stdout:
                print("✓ Already committed (no changes)")
            elif 'remote already exists' in result.stderr:
                print("✓ Remote already configured")
            else:
                print(f"⚠ {result.stderr}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()

print("=" * 50)
print("✓ Setup Complete!")
print("=" * 50)
print()
print("Your GLIS project is now on GitHub:")
print("https://github.com/tulwegroup/glis")
print()
