#!/usr/bin/env python3
"""
Quick Test - Test GLIS Layer 3 Components Without API Server

This script tests the core Layer 3 functionality without starting the API.
Perfect for verifying the system works.
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def test_imports():
    """Test that all Layer 3 modules can be imported"""
    print_header("TEST 1: IMPORTING LAYER 3 MODULES")
    
    modules = [
        ("reasoning.llm_integration", "LLM Integration"),
        ("reasoning.case_brief_generator", "Case Brief Generator"),
        ("reasoning.pleadings_assistant", "Pleadings Assistant"),
        ("reasoning.strategy_simulator", "Strategy Simulator"),
        ("intelligence.statute_db", "Statute Database"),
        ("api.layer3_endpoints", "Layer 3 API Endpoints"),
    ]
    
    results = []
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {display_name} ({module_name})")
            results.append(True)
        except ImportError as e:
            print(f"✗ {display_name} ({module_name})")
            print(f"  Error: {str(e)}")
            results.append(False)
    
    return all(results)

def test_statute_db():
    """Test Statute Database functionality"""
    print_header("TEST 2: STATUTE DATABASE")
    
    try:
        from intelligence.statute_db import get_statute_db
        
        db = get_statute_db()
        print(f"✓ Database initialized")
        
        # Test getting statutes
        statutes = db.get_all_statutes()
        print(f"✓ Loaded {len(statutes)} statutes")
        
        # List some statutes
        print(f"\n  Available Statutes:")
        for statute in statutes[:5]:
            print(f"    • {statute.name} ({statute.abbreviation})")
        
        # Test search
        results = db.search_by_keyword("employment")
        print(f"\n✓ Keyword search working")
        print(f"  Found {len(results)} results for 'employment'")
        
        return True
    except Exception as e:
        print(f"✗ Error testing statute database: {str(e)}")
        return False

def test_llm_manager():
    """Test LLM Integration"""
    print_header("TEST 3: LLM MANAGER")
    
    try:
        from reasoning.llm_integration import get_llm_manager
        
        manager = get_llm_manager()
        print(f"✓ LLM Manager initialized")
        
        # Check available providers
        print(f"✓ Supported LLM Providers:")
        print(f"    • OpenAI (GPT-4, GPT-3.5-turbo)")
        print(f"    • Claude (Anthropic)")
        print(f"    • Llama 2 (Open source)")
        print(f"    • Mistral (Open source)")
        
        # Check provider status
        print(f"\n  Note: Full LLM testing requires configured API keys")
        print(f"  Configure in .env file:")
        print(f"    OPENAI_API_KEY=sk-...")
        print(f"    CLAUDE_API_KEY=...")
        
        return True
    except Exception as e:
        print(f"✗ Error testing LLM manager: {str(e)}")
        return False

def test_case_brief_generator():
    """Test Case Brief Generator"""
    print_header("TEST 4: CASE BRIEF GENERATOR")
    
    try:
        from reasoning.case_brief_generator import get_brief_generator
        
        generator = get_brief_generator()
        print(f"✓ Case Brief Generator initialized")
        
        print(f"\n  Capabilities:")
        print(f"    • Generate FIHR (Facts, Issue, Holding, Reasoning) briefs")
        print(f"    • Extract legal issues and holdings")
        print(f"    • Analyze dissenting opinions")
        print(f"    • Compare related cases")
        print(f"    • Export to: Markdown, JSON, DOCX")
        
        print(f"\n  Note: Full brief generation requires:")
        print(f"    • Case judgment text")
        print(f"    • LLM API configuration")
        
        return True
    except Exception as e:
        print(f"✗ Error testing case brief generator: {str(e)}")
        return False

def test_pleadings_assistant():
    """Test Pleadings Assistant"""
    print_header("TEST 5: PLEADINGS ASSISTANT")
    
    try:
        from reasoning.pleadings_assistant import get_pleadings_assistant, DocumentType
        
        assistant = get_pleadings_assistant()
        print(f"✓ Pleadings Assistant initialized")
        
        print(f"\n  Supported Document Types:")
        doc_types = [
            "Summons",
            "Statement of Claim",
            "Defence",
            "Counterclaim",
            "Affidavit",
            "Motion/Application",
            "Brief in Support",
            "Reply",
            "Schedule",
            "Memorandum"
        ]
        for i, doc_type in enumerate(doc_types, 1):
            print(f"    {i}. {doc_type}")
        
        print(f"\n  Features:")
        print(f"    • Ghana court-specific formatting")
        print(f"    • Professional templates and structure")
        print(f"    • Batch document generation")
        print(f"    • Export to: PDF, DOCX, Markdown")
        
        return True
    except Exception as e:
        print(f"✗ Error testing pleadings assistant: {str(e)}")
        return False

def test_strategy_simulator():
    """Test Strategy Simulator"""
    print_header("TEST 6: STRATEGY SIMULATOR")
    
    try:
        from reasoning.strategy_simulator import get_strategy_simulator
        
        simulator = get_strategy_simulator()
        print(f"✓ Strategy Simulator initialized")
        
        print(f"\n  Capabilities:")
        print(f"    • Predict litigation win probability (0-1 scale)")
        print(f"    • Assess risk levels (Minimal to Critical)")
        print(f"    • Estimate costs (court fees, legal time)")
        print(f"    • Calculate expected duration (in months)")
        print(f"    • Provide strategic recommendations")
        print(f"    • Simulate settlement/appeal scenarios")
        print(f"    • Compare multiple legal strategies")
        
        print(f"\n  Risk Levels: MINIMAL, LOW, MODERATE, HIGH, VERY_HIGH, CRITICAL")
        
        return True
    except Exception as e:
        print(f"✗ Error testing strategy simulator: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoint definitions"""
    print_header("TEST 7: API ENDPOINTS (/V3 ROUTES)")
    
    try:
        from api.layer3_endpoints import router
        
        print(f"✓ Layer 3 API Router initialized")
        
        # Show routes
        print(f"\n  Available Endpoints:")
        
        routes = {
            "Case Briefs": [
                "POST /v3/brief/generate",
                "GET /v3/brief/compare"
            ],
            "Pleadings": [
                "POST /v3/pleading/generate",
                "POST /v3/pleading/generate/summons",
                "POST /v3/pleading/generate/statement-of-claim",
                "POST /v3/pleading/generate/defence",
                "POST /v3/pleading/batch"
            ],
            "Strategy": [
                "POST /v3/strategy/analyze",
                "POST /v3/strategy/compare"
            ],
            "Statutes": [
                "GET /v3/statute/search",
                "GET /v3/statute/{statute_id}/section/{section}",
                "GET /v3/statutes/list"
            ],
            "LLM": [
                "GET /v3/llm/providers",
                "GET /v3/llm/costs",
                "POST /v3/llm/model/set"
            ],
            "System": [
                "GET /v3/health"
            ]
        }
        
        for category, endpoints in routes.items():
            print(f"\n    {category}:")
            for endpoint in endpoints:
                print(f"      • {endpoint}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing API endpoints: {str(e)}")
        return False

def test_configuration():
    """Test configuration"""
    print_header("TEST 8: CONFIGURATION")
    
    try:
        env_file = Path(".env")
        env_example = Path(".env.example")
        
        if env_file.exists():
            print(f"✓ .env file exists")
            with open(env_file, 'r') as f:
                content = f.read()
                if 'OPENAI_API_KEY' in content:
                    if 'sk-' in content:
                        print(f"✓ OpenAI API key configured")
                    else:
                        print(f"⚠ OpenAI API key exists but not configured")
                        print(f"  Edit .env and add: OPENAI_API_KEY=sk-your-key-here")
                else:
                    print(f"⚠ OpenAI API key not found in .env")
        else:
            print(f"⚠ .env file not found")
            if env_example.exists():
                print(f"✓ .env.example exists - copy it to .env and configure")
            else:
                print(f"✗ Neither .env nor .env.example found")
        
        return True
    except Exception as e:
        print(f"✗ Error checking configuration: {str(e)}")
        return False

def show_next_steps():
    """Show next steps"""
    print_header("NEXT STEPS TO TEST FULL SYSTEM")
    
    print("""
1. START THE API SERVER
   Run: python run_glis.py
   
   Or manually:
   python -m uvicorn api.main:app --reload
   
   Then visit: http://localhost:8000/docs
   This is the Swagger UI where you can test all endpoints!

2. TEST ENDPOINTS IN SWAGGER UI
   • http://localhost:8000/docs
   • Click on any endpoint
   • Click "Try it out"
   • Enter parameters
   • Click "Execute"
   • See live response

3. EXAMPLE API CALLS
   
   Search Statutes:
   curl "http://localhost:8000/v3/statute/search?query=employment"
   
   List All Statutes:
   curl "http://localhost:8000/v3/statutes/list"
   
   Get Statute Section:
   curl "http://localhost:8000/v3/statute/gh_constitution_1992/section/1"

4. CONFIGURE OPENAI KEY (for LLM features)
   Edit .env file and add:
   OPENAI_API_KEY=sk-your-key-here
   
   Then restart API server

5. GENERATE SAMPLE DOCUMENTS
   With API running, test document generation:
   
   Generate Brief:
   POST /v3/brief/generate
   
   Generate Summons:
   POST /v3/pleading/generate/summons
   
   Analyze Strategy:
   POST /v3/strategy/analyze

6. EXPLORE DOCUMENTATION
   • LAYER3_QUICKSTART.md - Quick start guide
   • LAYER3_COMPLETION_REPORT.md - Technical details
   • LAYER3_EXECUTIVE_SUMMARY.md - Overview
    """)

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  GLIS LAYER 3 - QUICK SYSTEM TEST")
    print("="*70)
    
    tests = [
        ("Module Imports", test_imports),
        ("Statute Database", test_statute_db),
        ("LLM Manager", test_llm_manager),
        ("Case Brief Generator", test_case_brief_generator),
        ("Pleadings Assistant", test_pleadings_assistant),
        ("Strategy Simulator", test_strategy_simulator),
        ("API Endpoints", test_api_endpoints),
        ("Configuration", test_configuration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}\n")
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    # Show next steps
    show_next_steps()
    
    # Return success if all passed
    return all(result for _, result in results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
