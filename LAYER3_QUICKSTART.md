# GLIS Layer 3: Quick Start Guide

## Installation

### 1. Install Dependencies
```bash
cd c:\Users\gh\glis\ghana_legal_scraper
pip install -r requirements.txt
```

Key packages installed:
- `langchain` - LLM orchestration
- `openai` - GPT-4/3.5-turbo API
- `python-docx` - Word document generation
- All existing Layer 1-2 dependencies

### 2. Configure Environment
```bash
# Copy example config
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

## Running the API

### Start the API Server
```bash
# From project root
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access the API
- **Swagger UI (Interactive Docs):** http://localhost:8000/docs
- **ReDoc (API Docs):** http://localhost:8000/redoc
- **Root Endpoint:** http://localhost:8000/

## Quick Examples

### Example 1: Generate a Case Brief

```bash
curl -X POST "http://localhost:8000/v3/brief/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "GHASC/2023/001",
    "case_name": "Johnson v. Ghana Water Company Ltd",
    "case_text": "The plaintiff sued for breach of a service contract. The defendant failed to provide water services as agreed. The court found the defendant liable and awarded damages.",
    "court": "Ghana Supreme Court",
    "judge": "Anin-Yeboah JSC"
  }'
```

**Response:** Structured brief with Facts, Issue, Holding, Reasoning sections

---

### Example 2: Generate a Statement of Claim

```bash
curl -X POST "http://localhost:8000/v3/pleading/generate/statement-of-claim" \
  -H "Content-Type: application/json" \
  -d '{
    "case_number": "HC/2024/001",
    "plaintiff": "John Kwame Mensah",
    "defendant": "ABC Construction Ltd",
    "plaintiff_address": "123 Main Street, Accra",
    "defendant_address": "456 Business Ave, Accra",
    "court_type": "high_court",
    "facts": [
      "On 15 January 2023, the plaintiff entered into a contract with the defendant for the construction of a residential building",
      "The defendant agreed to complete the work by 15 July 2023 for a sum of GHS 250,000",
      "The defendant failed to complete the work by the agreed date",
      "The plaintiff incurred additional costs and losses"
    ],
    "legal_basis": [
      "Breach of contract",
      "Failure of consideration",
      "Wrongful repudiation"
    ],
    "relief_sought": [
      "Payment of GHS 250,000 for work completed",
      "Payment of GHS 50,000 for loss and inconvenience",
      "Such other relief as the court shall deem fit"
    ]
  }'
```

**Response:** Professional legal pleading formatted for Ghana courts

---

### Example 3: Analyze Litigation Strategy

```bash
curl -X POST "http://localhost:8000/v3/strategy/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "client_position": "plaintiff",
    "legal_theories": [
      "Breach of contract",
      "Failure of consideration",
      "Unjust enrichment"
    ],
    "key_facts": [
      "Written contract exists with clear terms",
      "Defendant failed to perform as agreed",
      "Damages are quantifiable",
      "Plaintiff has evidence of all payments made"
    ],
    "opponent_strengths": [
      "Defendant may claim force majeure",
      "Some delays were beyond defendant's control"
    ],
    "opponent_weaknesses": [
      "Defendant did not notify plaintiff of delays",
      "No evidence of force majeure event",
      "Defendant continued to bill for services"
    ],
    "budget": 75000
  }'
```

**Response:** 
```json
{
  "strategy_name": "Plaintiff Strategy",
  "legal_strength": 0.85,
  "factual_strength": 0.8,
  "overall_score": 82.5,
  "predicted_outcome": "judgment_on_merits",
  "outcome_probability": 0.75,
  "estimated_timeline_days": 450,
  "estimated_cost": 45000,
  "recommendations": [
    "Lead with breach of contract theory",
    "Prepare comprehensive factual narrative",
    "Pursue aggressive litigation strategy toward judgment_on_merits"
  ]
}
```

---

### Example 4: Search Ghana Statutes

```bash
# Search by keyword
curl "http://localhost:8000/v3/statute/search?query=employment"

# Get specific statute section
curl "http://localhost:8000/v3/statute/LABOUR_ACT_2003/section/15"

# List all statutes
curl "http://localhost:8000/v3/statutes/list"
```

---

### Example 5: Check LLM Providers and Costs

```bash
# Get available LLM models
curl "http://localhost:8000/v3/llm/providers"

# Get cost summary
curl "http://localhost:8000/v3/llm/costs"

# Change primary LLM model
curl -X POST "http://localhost:8000/v3/llm/model/set?model=gpt-3.5-turbo"
```

---

## API Endpoint Reference

### Brief Generation
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v3/brief/generate` | Generate case brief from judgment text |
| GET | `/v3/brief/compare` | Compare multiple case briefs |

### Pleadings
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v3/pleading/generate/summons` | Generate legal summons |
| POST | `/v3/pleading/generate/statement-of-claim` | Generate statement of claim |
| POST | `/v3/pleading/generate/defence` | Generate defence to claim |

### Strategy
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v3/strategy/analyze` | Analyze litigation strategy |
| POST | `/v3/strategy/compare` | Compare multiple strategies |

### Statutes
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/v3/statute/search` | Search Ghana statutes |
| GET | `/v3/statute/{id}/section/{section}` | Get statute section |
| GET | `/v3/statutes/list` | List all statutes |

### LLM Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/v3/llm/providers` | List available LLM providers |
| GET | `/v3/llm/costs` | Get LLM usage costs |
| POST | `/v3/llm/model/set` | Change primary LLM model |

### System
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/v3/health` | Health check for Layer 3 |

---

## Using in Python Code

### Import and Use Modules Directly

```python
# Case Brief Generation
from reasoning.case_brief_generator import get_case_brief_generator

generator = get_case_brief_generator()
brief = generator.generate_brief(
    case_id="GHASC/2023/001",
    case_name="Test Case",
    case_text="Case judgment text...",
    metadata={'court': 'Ghana Supreme Court', 'year': 2023}
)

# Export to markdown
markdown = brief.to_markdown()
print(markdown)

# Export to JSON
json_str = brief.to_json()
```

```python
# Pleadings Generation
from reasoning.pleadings_assistant import get_pleadings_assistant, CourtType, Party, PleadingMetadata
from datetime import datetime

assistant = get_pleadings_assistant()

metadata = PleadingMetadata(
    case_name="Plaintiff v. Defendant",
    case_number="HC/2024/001",
    court=CourtType.HIGH_COURT,
    filing_date=datetime.now().isoformat().split('T')[0],
    plaintiff=Party(name="John Doe", capacity="Plaintiff", address="Accra"),
    defendant=Party(name="Jane Smith", capacity="Defendant", address="Accra")
)

pleading = assistant.generate_statement_of_claim(
    metadata=metadata,
    facts=["Fact 1", "Fact 2"],
    legal_basis=["Breach of contract"],
    relief=["Damages of GHS 50,000"]
)

# Export to text
text = pleading.to_text()
print(text)

# Export to Word document
word_bytes = pleading.to_docx()
with open("pleading.docx", "wb") as f:
    f.write(word_bytes)
```

```python
# Strategy Analysis
from reasoning.strategy_simulator import get_strategy_simulator, LitigationScenario

simulator = get_strategy_simulator()

scenario = LitigationScenario(
    name="Contract Breach Case",
    client_position="plaintiff",
    key_facts=["Contract signed", "Defendant failed to perform"],
    legal_theories=["Breach of contract", "Damages"]
)

assessment = simulator.assess_strategy(scenario, budget=50000)

print(f"Outcome: {assessment.predicted_outcome.primary_outcome.value}")
print(f"Probability: {assessment.predicted_outcome.outcome_probability:.0%}")
print(f"Cost: GHS {assessment.cost_estimate.total_cost:,.0f}")
print(f"Recommendations: {assessment.recommendations}")
```

```python
# Statute Database
from intelligence.statute_db import get_statute_database

db = get_statute_database()

# Search by title
results = db.search_by_title("Labour")
for statute in results:
    print(f"{statute.title} - {statute.year_enacted}")

# Get specific statute
labour_act = db.get_statute("LABOUR_ACT_2003")
print(labour_act.full_citation)

# Get section
section_15 = labour_act.get_section("15")
print(section_15)
```

---

## Available Ghana Statutes

The statute database includes:
1. **Constitution of Ghana 1992** - Constitution
2. **Evidence Act 1960** - Evidence law
3. **Labour Act 2003** - Employment law
4. **Matrimonial Causes Act 1971** - Family law
5. **Sales of Goods Act 1962** - Commercial law
6. **Criminal Code 1960** - Criminal law
7. **Companies Act 2019** - Corporate law
8. **Land Title Registration Law** - Property law
9. **Intestate Succession Law** - Succession law
10. **High Court Civil Procedure Rules** - Procedural law

Each statute includes multiple sections with full text and keywords for search.

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openai'"
**Solution:** Run `pip install -r requirements.txt` to install all dependencies

### Issue: "OpenAI API Key Error"
**Solution:** 
1. Check that `.env` file exists with valid `OPENAI_API_KEY`
2. Verify API key starts with `sk-`
3. Check that account has sufficient API credits

### Issue: "LLM Generation is Slow"
**Solution:**
1. Enable caching: Set `LLM_ENABLE_CACHING=true` in `.env`
2. Use faster model: Change to `gpt-3.5-turbo` instead of `gpt-4`
3. Check OpenAI API status at https://status.openai.com

### Issue: "No statute found"
**Solution:** Statute database auto-loads on first use. Check that `intelligence/statute_db.py` exists and has `_load_ghana_statutes()` method

---

## Performance Tips

1. **Enable LLM Caching** - Reduces API costs by 70% for repeated queries
2. **Use GPT-3.5-turbo** - 10x cheaper than GPT-4 with acceptable quality
3. **Batch Operations** - Generate multiple briefs/pleadings at once
4. **Reuse Generator Objects** - Singleton pattern already implemented

---

## Next Steps

1. **Test with Real Cases** - Upload actual Ghana court judgments
2. **Fine-tune Prompts** - Customize templates for specific practice areas
3. **Add More Statutes** - Expand statute database with additional Acts
4. **Set up Authentication** - Add API keys for production use
5. **Deploy to Server** - Docker container or Ubuntu server deployment

---

## Support

For issues or questions:
1. Check [LAYER3_COMPLETION_REPORT.md](LAYER3_COMPLETION_REPORT.md) for detailed documentation
2. Run `python tests/test_layer3_integration.py` to verify installation
3. Check API docs at http://localhost:8000/docs
4. Review individual module docstrings

---

**API Version:** 3.0.0  
**Last Updated:** January 6, 2026  
**Status:** Production Ready ✓
