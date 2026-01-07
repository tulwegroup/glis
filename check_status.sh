#!/bin/bash
cd /c/Users/gh/glis/ghana_legal_scraper
echo "=== Git Status ==="
git status --short
echo ""
echo "=== Commit Details ==="
git log --oneline -1
echo ""
echo "=== Page.tsx First 5 Lines ==="
head -5 app/page.tsx
