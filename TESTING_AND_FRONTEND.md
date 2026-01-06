# GLIS Frontend & System Testing Guide

## Overview

The **Ghana Legal Intelligence System (GLIS)** is a complete 3-layer legal AI platform. This guide shows you how to test and interact with the system, especially the **interactive API frontend** (Swagger UI).

---

## What is the "Frontend"?

Unlike traditional web apps with a graphical user interface (buttons, forms, etc.), GLIS uses an **Interactive API Documentation** as its frontend:

### **Swagger UI (Recommended)**
- **URL**: `http://localhost:8000/docs`
- **Purpose**: Interactive API documentation and testing
- Interactive "Try it out" buttons for each endpoint
- Real-time request/response testing
- Automatic parameter validation
- Beautiful, professional interface

### **ReDoc** (Alternative)
- **URL**: `http://localhost:8000/redoc`
- **Purpose**: Clean, readable API documentation
- Best for reading documentation
- Less interactive than Swagger

---

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output**: All packages installed successfully

### Step 2: Configure Environment

```bash
# Copy configuration template
cp .env.example .env

# Edit .env and add your OpenAI API key (if you have one)
# OPENAI_API_KEY=sk-your-key-here
```

**Note**: System works without API key (limited LLM features)

### Step 3: Run Quick Test

```bash
python quick_test.py
```

**Expected output**:
```
✓ Test 1: IMPORTING LAYER 3 MODULES
  ✓ LLM Integration
  ✓ Case Brief Generator
  ✓ Pleadings Assistant
  ✓ Strategy Simulator
  ✓ Statute Database
  ✓ API Endpoints

✓ Test 2: STATUTE DATABASE
  ✓ Database initialized
  ✓ Loaded 10+ statutes

...and more tests
```

### Step 4: Start API Server

**Option A - Use Startup Script**:
```bash
python run_glis.py
```

**Option B - Manual Start**:
```bash
python -m uvicorn api.main:app --reload
```

**Expected output**:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 5: Open the Frontend

**Visit**: http://localhost:8000/docs

You should see the **Swagger UI** with all available endpoints!

---

## Testing Endpoints via Swagger UI

### Example 1: Search Ghana Statutes

1. **Navigate to**: `/v3/statute/search` (GET)
2. **Click**: "Try it out" button
3. **Enter**: `employment` in the query field
4. **Click**: "Execute"
5. **View**: JSON response with matching statutes

**Sample Response**:
```json
{
  "query": "employment",
  "results": [
    {
      "statute_id": "gh_labour_act_2003",
      "name": "Labour Act, 2003",
      "abbreviation": "NRCD 652",
      "relevance_score": 0.95,
      "matching_sections": [
        {
          "section": "1",
          "title": "Scope of Act",
          "preview": "This Act applies to employment relationships..."
        }
      ]
    }
  ],
  "total_results": 12
}
```

### Example 2: Get Statute List

1. **Navigate to**: `/v3/statutes/list` (GET)
2. **Click**: "Try it out"
3. **Click**: "Execute"
4. **View**: Complete list of all Ghana statutes in database

**Sample Response**:
```json
{
  "statutes": [
    {
      "statute_id": "gh_constitution_1992",
      "name": "1992 Constitution of Ghana",
      "abbreviation": "Const. 1992",
      "year": 1992,
      "sections_count": 308
    },
    {
      "statute_id": "gh_labour_act_2003",
      "name": "Labour Act, 2003",
      "abbreviation": "NRCD 652",
      "year": 2003,
      "sections_count": 150
    }
    // ... more statutes
  ],
  "total_count": 10
}
```

### Example 3: Get Specific Statute Section

1. **Navigate to**: `/v3/statute/{statute_id}/section/{section}` (GET)
2. **Click**: "Try it out"
3. **Enter**: 
   - `statute_id`: `gh_constitution_1992`
   - `section`: `1`
4. **Click**: "Execute"
5. **View**: Full text of that statute section

**Sample Response**:
```json
{
  "statute": "1992 Constitution of Ghana",
  "section": "1",
  "title": "Preamble",
  "text": "The sovereignty of Ghana resides in the people of Ghana in whose name this Constitution is made...",
  "subsections": [
    {
      "subsection": "1",
      "text": "Ghana shall be a sovereign unitary state..."
    }
  ],
  "effective_date": "1992-01-07"
}
```

---

## Testing Endpoints via curl

### Search Statutes

```bash
curl "http://localhost:8000/v3/statute/search?query=employment" | python -m json.tool
```

### List All Statutes

```bash
curl "http://localhost:8000/v3/statutes/list" | python -m json.tool
```

### Get Constitution Section 1

```bash
curl "http://localhost:8000/v3/statute/gh_constitution_1992/section/1" | python -m json.tool
```

### Check LLM Providers (if configured)

```bash
curl "http://localhost:8000/v3/llm/providers" | python -m json.tool
```

### Check System Health

```bash
curl "http://localhost:8000/v3/health" | python -m json.tool
```

---

## Available Endpoints Summary

### Case Briefs `/v3/brief/`
- `POST /v3/brief/generate` - Generate case brief from judgment text
- `GET /v3/brief/compare` - Compare multiple case briefs

### Pleadings `/v3/pleading/`
- `POST /v3/pleading/generate` - Generic document generator
- `POST /v3/pleading/generate/summons` - Generate legal summons
- `POST /v3/pleading/generate/statement-of-claim` - Generate statement of claim
- `POST /v3/pleading/generate/defence` - Generate defence document
- `POST /v3/pleading/generate/affidavit` - Generate affidavit
- `POST /v3/pleading/batch` - Batch generate multiple documents

### Litigation Strategy `/v3/strategy/`
- `POST /v3/strategy/analyze` - Analyze litigation strategy & predict outcomes
- `POST /v3/strategy/compare` - Compare multiple legal strategies

### Statutes `/v3/statute/`
- `GET /v3/statute/search` - Search Ghana statutes by keyword
- `GET /v3/statute/{statute_id}/section/{section}` - Get specific statute section
- `GET /v3/statutes/list` - List all available statutes
- `POST /v3/statute/interpret` - Get LLM interpretation of statute (requires API key)

### LLM Management `/v3/llm/`
- `GET /v3/llm/providers` - List available LLM providers
- `GET /v3/llm/costs` - Check API usage costs
- `POST /v3/llm/model/set` - Change primary LLM model

### System `/v3/`
- `GET /v3/health` - Health check for Layer 3

---

## Advanced Testing

### Generate Case Brief (requires LLM API key)

**Via Swagger UI**:
1. Navigate to `POST /v3/brief/generate`
2. Click "Try it out"
3. Enter sample data:
```json
{
  "case_id": "GHASC/2023/001",
  "case_name": "ABC Ltd v. XYZ Ltd",
  "case_text": "Facts: The appellant entered into a contract with the respondent... Issue: Whether the contract was enforceable... Holding: The contract was enforceable... Reasoning: ...",
  "court": "Ghana Supreme Court"
}
```
4. Click "Execute"
5. View generated brief in FIHR format

**Via curl**:
```bash
curl -X POST "http://localhost:8000/v3/brief/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "GHASC/2023/001",
    "case_name": "Test Case",
    "case_text": "Case judgment text here...",
    "court": "Ghana Supreme Court"
  }' | python -m json.tool
```

### Generate Legal Document

**Via Swagger UI**:
1. Navigate to `POST /v3/pleading/generate/summons`
2. Click "Try it out"
3. Enter details (claimant, defendant, amount, etc.)
4. Click "Execute"
5. View generated summons document

### Analyze Litigation Strategy

**Via Swagger UI**:
1. Navigate to `POST /v3/strategy/analyze`
2. Click "Try it out"
3. Enter case details and strategy parameters
4. Click "Execute"
5. View strategy analysis with:
   - Win probability (0-1)
   - Risk level
   - Estimated costs
   - Duration estimate
   - Strategic recommendations

---

## Troubleshooting

### Problem: "Cannot connect to localhost:8000"

**Solution**:
1. Check if API server is running: `python run_glis.py`
2. Check if port 8000 is free: `netstat -ano | findstr :8000` (Windows)
3. Try different port: `python -m uvicorn api.main:app --port 8001`

### Problem: "ModuleNotFoundError"

**Solution**:
1. Ensure you're in project directory
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (needs 3.8+)

### Problem: "OpenAI API error"

**Solution**:
1. Most endpoints work without API key
2. LLM features require configured API key in `.env`
3. Add to `.env`: `OPENAI_API_KEY=sk-your-key-here`
4. Restart API server

### Problem: "Swagger UI won't load"

**Solution**:
1. Check API is running: `curl http://localhost:8000/`
2. Try ReDoc instead: `http://localhost:8000/redoc`
3. Clear browser cache and reload
4. Try different browser

---

## Key Features to Test

### ✓ Statute Database
- [x] Search by keyword
- [x] Get specific sections
- [x] List all statutes
- [x] View statute details

### ✓ Case Briefs
- [x] Generate FIHR briefs (requires LLM key)
- [x] Compare cases
- [x] Export formats

### ✓ Pleadings
- [x] Generate summons
- [x] Generate statements of claim
- [x] Generate defence documents
- [x] Batch operations

### ✓ Strategy Analysis
- [x] Predict outcomes
- [x] Assess risk levels
- [x] Estimate costs
- [x] Compare strategies

### ✓ LLM Integration
- [x] Multiple provider support
- [x] Cost tracking
- [x] Fallback chains
- [x] Caching

---

## Documentation Files

For more detailed information, see:

- **LAYER3_QUICKSTART.md** - Quick reference guide
- **LAYER3_COMPLETION_REPORT.md** - Technical deep dive
- **LAYER3_EXECUTIVE_SUMMARY.md** - Business overview

---

## Next Steps

1. **Run the System**: `python run_glis.py`
2. **Open Frontend**: http://localhost:8000/docs
3. **Test Endpoints**: Use "Try it out" buttons
4. **Explore Features**: Try different endpoint combinations
5. **Add API Key** (optional): For advanced LLM features
6. **Read Docs**: Check LAYER3_QUICKSTART.md for more examples

---

## Questions?

All 13 endpoints are fully documented in Swagger UI with:
- Description of what each endpoint does
- Parameter definitions
- Example request/response
- Error codes and meanings

**Visit http://localhost:8000/docs** to explore!

---

**System Status**: ✓ Ready to Test  
**Total Endpoints**: 13  
**Statutes Available**: 10+  
**Document Types**: 10  
**LLM Providers**: 5
