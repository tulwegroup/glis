#!/usr/bin/env python3
import subprocess
import os

os.chdir('c:\\Users\\gh\\glis\\ghana_legal_scraper')

# Stage all changes
subprocess.run(['git', 'add', '.'], check=False)

# Check status
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print("Status:", result.stdout)

# Commit with force if needed
result = subprocess.run(
    ['git', 'commit', '-m', 'Update dashboard UI: Add functional legal tools interface'],
    capture_output=True, text=True, timeout=30
)

if 'nothing to commit' in result.stdout.lower() or 'nothing to commit' in result.stderr.lower():
    print("No changes to commit")
else:
    print("Commit:", result.stdout)
    print("Error:", result.stderr)

# Push  
result = subprocess.run(
    ['git', 'push', 'origin', 'main'],
    capture_output=True, text=True, timeout=30
)
print("Push stdout:", result.stdout)
print("Push stderr:", result.stderr)
print("Push return code:", result.returncode)

# Show final log
result = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True)
print("Final commit:", result.stdout)
