#!/usr/bin/env python3
"""
Test script to verify Railway backend is running and accessible
"""
import requests
import time
import sys

# Replace this with your Railway backend URL from deployment logs
RAILWAY_URL = input("Enter your Railway backend URL (e.g., https://glis-backend-xyz.railway.app): ").strip()

if not RAILWAY_URL.startswith("http"):
    RAILWAY_URL = f"https://{RAILWAY_URL}"

print(f"\n🔍 Testing Railway backend at: {RAILWAY_URL}\n")

# Test 1: Health check
print("1️⃣  Testing /health endpoint...")
try:
    response = requests.get(f"{RAILWAY_URL}/health", timeout=5)
    if response.status_code == 200:
        print(f"   ✅ Health check passed: {response.json()}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Could not reach health endpoint: {e}")

# Test 2: Root endpoint
print("\n2️⃣  Testing / (root) endpoint...")
try:
    response = requests.get(f"{RAILWAY_URL}/", timeout=5)
    if response.status_code == 200:
        print(f"   ✅ Root endpoint working: {response.json()}")
    else:
        print(f"   ❌ Root endpoint failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Could not reach root endpoint: {e}")

# Test 3: Semantic search
print("\n3️⃣  Testing /api/search/semantic endpoint...")
try:
    payload = {
        "query": "What are the rights of workers in Ghana?",
        "k": 3
    }
    response = requests.post(
        f"{RAILWAY_URL}/api/search/semantic",
        json=payload,
        timeout=10
    )
    if response.status_code == 200:
        print(f"   ✅ Semantic search working!")
        result = response.json()
        print(f"   Answer: {result.get('answer', 'N/A')[:100]}...")
        print(f"   Confidence: {result.get('confidence_score', 'N/A')}")
    else:
        print(f"   ❌ Semantic search failed: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Could not reach semantic search: {e}")

print("\n" + "="*60)
print("✅ If all tests pass, backend is ready!")
print("📝 Update .env.local with: NEXT_PUBLIC_API_URL=" + RAILWAY_URL)
