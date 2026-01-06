#!/usr/bin/env python3
"""
GLIS System Startup Script

This script starts the API and guides you through the testing process.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_dependencies():
    """Check if required packages are installed"""
    print_header("CHECKING DEPENDENCIES")
    
    required = ['fastapi', 'uvicorn', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print(f"\nRun: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists"""
    print_header("CHECKING ENVIRONMENT CONFIGURATION")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print(f"✗ .env file not found")
            print(f"✓ .env.example exists")
            print(f"\nCreating .env from template...")
            import shutil
            shutil.copy(env_example, env_file)
            print(f"✓ .env file created")
            
            print(f"\n⚠ IMPORTANT: Configure your OpenAI API Key")
            print(f"  1. Edit .env file")
            print(f"  2. Add: OPENAI_API_KEY=sk-your-key-here")
            print(f"  3. Save and restart API")
            return True
        else:
            print(f"✗ Neither .env nor .env.example found")
            return False
    else:
        print(f"✓ .env file exists")
        
        # Check for API key
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content and 'sk-' in content:
                print(f"✓ OPENAI_API_KEY configured")
            else:
                print(f"⚠ OPENAI_API_KEY not configured or invalid")
                print(f"  Some features will be limited without this key")
        
        return True

def start_api_server():
    """Start the FastAPI server"""
    print_header("STARTING API SERVER")
    
    print("Starting API on http://localhost:8000...")
    print("This will run in the background.")
    
    try:
        # Use subprocess to start the server
        process = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'api.main:app', '--host', '0.0.0.0', '--port', '8000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("Waiting for server to start (5 seconds)...")
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✓ API Server Started Successfully!")
            print(f"✓ Process ID: {process.pid}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"✗ Server failed to start")
            print(f"Error: {stderr.decode()}")
            return None
    
    except Exception as e:
        print(f"✗ Failed to start server: {str(e)}")
        return None

def show_welcome():
    """Show welcome message"""
    print_header("GLIS LAYER 3 SYSTEM - WELCOME")
    
    print("""
    Ghana Legal Intelligence System (GLIS)
    Advanced Legal Analysis & Intelligence Platform
    
    This system includes:
    • Case Brief Generator - Automatic brief generation from judgments
    • Pleadings Assistant - Professional legal document generation
    • Strategy Simulator - Litigation outcome prediction & analysis
    • Statute Database - Comprehensive Ghana legal database
    • LLM Integration - Advanced AI-powered analysis
    
    All features are accessible via REST API with interactive documentation.
    """)

def show_api_endpoints():
    """Show available API endpoints"""
    print_header("AVAILABLE API ENDPOINTS")
    
    endpoints = {
        "Case Briefs": [
            "POST /v3/brief/generate - Generate case brief from judgment",
            "GET /v3/brief/compare - Compare multiple briefs"
        ],
        "Pleadings": [
            "POST /v3/pleading/generate/summons - Generate legal summons",
            "POST /v3/pleading/generate/statement-of-claim - Generate statement of claim",
            "POST /v3/pleading/generate/defence - Generate defence"
        ],
        "Litigation Strategy": [
            "POST /v3/strategy/analyze - Analyze litigation strategy",
            "POST /v3/strategy/compare - Compare multiple strategies"
        ],
        "Statute Database": [
            "GET /v3/statute/search - Search Ghana statutes",
            "GET /v3/statute/{id}/section/{section} - Get statute section",
            "GET /v3/statutes/list - List all available statutes"
        ],
        "LLM Management": [
            "GET /v3/llm/providers - List available LLM providers",
            "GET /v3/llm/costs - Get LLM usage costs",
            "POST /v3/llm/model/set - Change primary LLM model"
        ],
        "System": [
            "GET /v3/health - Layer 3 health check",
            "GET /health - API health check",
            "GET / - API information"
        ]
    }
    
    for category, methods in endpoints.items():
        print(f"\n{category}:")
        for method in methods:
            print(f"  • {method}")

def show_next_steps():
    """Show next steps for user"""
    print_header("NEXT STEPS")
    
    print("""
1. OPEN INTERACTIVE API DOCUMENTATION
   • Visit: http://localhost:8000/docs
   • This is the Swagger UI where you can test all endpoints
   • Try different endpoints and see responses in real-time

2. RUN SYSTEM TESTS
   • In another terminal, run:
     python test_layer3_system.py
   • This will test all Layer 3 components

3. TEST SPECIFIC ENDPOINTS
   
   a) Search Ghana Statutes:
      curl "http://localhost:8000/v3/statute/search?query=employment"
   
   b) Get Statute List:
      curl "http://localhost:8000/v3/statutes/list"
   
   c) Check LLM Providers:
      curl "http://localhost:8000/v3/llm/providers"
   
   d) Analyze Litigation Strategy:
      curl -X POST "http://localhost:8000/v3/strategy/analyze" \\
        -H "Content-Type: application/json" \\
        -d '{
          "client_position": "plaintiff",
          "legal_theories": ["Breach of contract"],
          "key_facts": ["Fact 1", "Fact 2"],
          "budget": 50000
        }'

4. GENERATE CASE BRIEF (requires OpenAI API key)
   curl -X POST "http://localhost:8000/v3/brief/generate" \\
     -H "Content-Type: application/json" \\
     -d '{
       "case_id": "GHASC/2023/001",
       "case_name": "Test v. Defendant",
       "case_text": "Case judgment text...",
       "court": "Ghana Supreme Court"
     }'

5. CONFIGURE OPENAI API KEY (for full LLM features)
   • Edit .env file
   • Add: OPENAI_API_KEY=sk-your-key-here
   • Restart API

6. EXPLORE DOCUMENTATION
   • Visit: http://localhost:8000/docs (Swagger UI)
   • Visit: http://localhost:8000/redoc (ReDoc)
   • Read: LAYER3_QUICKSTART.md
   • Read: LAYER3_COMPLETION_REPORT.md
    """)

def main():
    """Main startup process"""
    
    # Show welcome
    show_welcome()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check environment
    if not check_env_file():
        print("\n❌ Environment setup failed")
        return False
    
    # Start API
    process = start_api_server()
    if not process:
        print("\n❌ Failed to start API server")
        print("\nTroubleshooting:")
        print("  1. Make sure you're in the project directory")
        print("  2. Try running manually: python -m uvicorn api.main:app --reload")
        print("  3. Check that port 8000 is not in use")
        return False
    
    # Show endpoints
    show_api_endpoints()
    
    # Show next steps
    show_next_steps()
    
    # Offer to open browser
    print("\n" + "="*70)
    time.sleep(2)
    
    try:
        response = input("Open API documentation in browser? (y/n): ").lower().strip()
        if response == 'y':
            print("Opening http://localhost:8000/docs in browser...")
            webbrowser.open("http://localhost:8000/docs")
            time.sleep(2)
    except:
        pass
    
    print("\n" + "="*70)
    print("✓ GLIS API is running!")
    print("✓ API URL: http://localhost:8000")
    print("✓ Documentation: http://localhost:8000/docs")
    print("="*70)
    print("\nServer is running. Press Ctrl+C to stop.\n")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down API server...")
        process.terminate()
        process.wait()
        print("✓ API server stopped")
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
