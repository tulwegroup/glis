"""
Integration Tests for Layer 3 - Reasoning & Advanced Intelligence

Tests all new modules and API endpoints to ensure proper integration.
"""

import json
from datetime import datetime
from pathlib import Path

# Layer 3 module imports
from reasoning.llm_integration import (
    get_llm_orchestrator,
    LLMConfig,
    ModelProvider,
    TaskType
)
from reasoning.case_brief_generator import get_case_brief_generator
from reasoning.pleadings_assistant import (
    get_pleadings_assistant,
    PleadingType,
    CourtType,
    Party,
    PleadingMetadata
)
from reasoning.strategy_simulator import (
    get_strategy_simulator,
    LitigationScenario,
    RiskLevel
)
from intelligence.statute_db import (
    get_statute_database,
    StatuteType
)


def test_llm_integration():
    """Test LLM integration and provider initialization"""
    print("\n" + "="*70)
    print("TEST 1: LLM Integration")
    print("="*70)
    
    try:
        orchestrator = get_llm_orchestrator()
        
        # Check available providers
        providers = orchestrator.available_providers()
        print(f"✓ Available LLM providers: {len(providers)}")
        for p in providers:
            print(f"  - {p.value}")
        
        # Check prompt templates
        templates = orchestrator.prompt_templates
        print(f"✓ Loaded {len(templates)} prompt templates")
        print(f"  Templates: {', '.join(list(templates.keys())[:5])}")
        
        # Check cost tracking
        cost_summary = orchestrator.get_cost_summary()
        print(f"✓ Cost tracking initialized: ${cost_summary['total_cost_usd']:.2f}")
        
        print("✓ LLM Integration: PASSED\n")
        return True
    
    except Exception as e:
        print(f"✗ LLM Integration: FAILED - {str(e)}\n")
        return False


def test_case_brief_generator():
    """Test case brief generation"""
    print("="*70)
    print("TEST 2: Case Brief Generator")
    print("="*70)
    
    try:
        generator = get_case_brief_generator()
        print("✓ Case brief generator initialized")
        
        # Test brief object creation (no LLM call)
        test_case = {
            'case_id': 'GHASC/2023/001',
            'case_name': 'Test v. Defendant',
            'case_text': 'This is a test case about breach of contract. The defendant failed to pay agreed amount.',
            'metadata': {
                'court': 'Ghana Supreme Court',
                'year': 2023,
                'date_decided': '2023-01-15',
                'judge': 'Anin-Yeboah JSC'
            }
        }
        
        print("✓ Test case data prepared")
        print(f"  Case ID: {test_case['case_id']}")
        print(f"  Case Name: {test_case['case_name']}")
        
        # Check markdown export method
        from reasoning.case_brief_generator import CaseBrief, BriefSection
        test_brief = CaseBrief(
            case_id='GHASC/2023/001',
            case_name='Test Case',
            court='Ghana Supreme Court',
            year=2023,
            date_decided='2023-01-15',
            judge='Test Judge',
            facts=BriefSection(title='Facts', content='Test facts'),
            issue=BriefSection(title='Issue', content='Test issue'),
            holding=BriefSection(title='Holding', content='Test holding'),
            reasoning=BriefSection(title='Reasoning', content='Test reasoning')
        )
        
        markdown = test_brief.to_markdown()
        print(f"✓ Brief markdown export: {len(markdown)} characters")
        
        print("✓ Case Brief Generator: PASSED\n")
        return True
    
    except Exception as e:
        print(f"✗ Case Brief Generator: FAILED - {str(e)}\n")
        return False


def test_pleadings_assistant():
    """Test pleadings document generation"""
    print("="*70)
    print("TEST 3: Pleadings Assistant")
    print("="*70)
    
    try:
        assistant = get_pleadings_assistant()
        print("✓ Pleadings assistant initialized")
        
        # Check available court types
        courts = [ct for ct in CourtType]
        print(f"✓ Available court types: {len(courts)}")
        print(f"  Courts: {', '.join([ct.value for ct in courts[:3]])}")
        
        # Check pleading types
        pleading_types = [pt for pt in PleadingType]
        print(f"✓ Available pleading types: {len(pleading_types)}")
        print(f"  Types: {', '.join([pt.value for pt in pleading_types[:5]])}")
        
        # Check court formats
        formats = len(assistant.court_formats)
        print(f"✓ Court formats loaded: {formats}")
        
        # Check pleading templates
        templates = len(assistant.templates)
        print(f"✓ Pleading templates loaded: {templates}")
        
        # Test party object
        party = Party(
            name="John Doe",
            capacity="Plaintiff",
            address="123 Main Street, Accra",
            lawyer="Jane Smith"
        )
        print(f"✓ Test party created: {party.name} ({party.capacity})")
        
        print("✓ Pleadings Assistant: PASSED\n")
        return True
    
    except Exception as e:
        print(f"✗ Pleadings Assistant: FAILED - {str(e)}\n")
        return False


def test_strategy_simulator():
    """Test litigation strategy simulation"""
    print("="*70)
    print("TEST 4: Strategy Simulator")
    print("="*70)
    
    try:
        simulator = get_strategy_simulator()
        print("✓ Strategy simulator initialized")
        
        # Create test scenario
        scenario = LitigationScenario(
            name="Contract Breach Case",
            client_position="plaintiff",
            key_facts=[
                "Contract signed on 2023-01-15",
                "Defendant failed to perform on 2023-06-30",
                "Damages quantified at GHS 50,000"
            ],
            legal_theories=["Breach of contract", "Failure of consideration"],
            opponent_strengths=["Statute of limitations defense"],
            opponent_weaknesses=["Clear breach of terms"]
        )
        
        print(f"✓ Test scenario created: {scenario.name}")
        print(f"  Client position: {scenario.client_position}")
        print(f"  Legal theories: {len(scenario.legal_theories)}")
        
        # Test strategy assessment
        assessment = simulator.assess_strategy(scenario, budget=50000.0)
        
        print(f"✓ Strategy assessment generated")
        print(f"  Legal strength: {assessment.legal_strength:.2f}")
        print(f"  Factual strength: {assessment.factual_strength:.2f}")
        print(f"  Overall score: {assessment.overall_score:.1f}")
        print(f"  Predicted outcome: {assessment.predicted_outcome.primary_outcome.value}")
        print(f"  Outcome probability: {assessment.predicted_outcome.outcome_probability:.2f}")
        print(f"  Estimated cost: GHS {assessment.cost_estimate.total_cost:.2f}")
        print(f"  Timeline: {assessment.predicted_outcome.timeline_estimate} days")
        
        # Check risk assessment
        risk_data = assessment.risk_assessment
        print(f"✓ Risk assessment: {risk_data['risk_level']} (score: {risk_data['risk_score']})")
        
        # Check recommendations
        print(f"✓ Generated {len(assessment.recommendations)} recommendations")
        for i, rec in enumerate(assessment.recommendations[:3], 1):
            print(f"  {i}. {rec}")
        
        print("✓ Strategy Simulator: PASSED\n")
        return True
    
    except Exception as e:
        print(f"✗ Strategy Simulator: FAILED - {str(e)}\n")
        return False


def test_statute_database():
    """Test statute database and search"""
    print("="*70)
    print("TEST 5: Statute Database")
    print("="*70)
    
    try:
        db = get_statute_database()
        print("✓ Statute database initialized")
        
        # List all statutes
        all_statutes = db.list_all_statutes()
        print(f"✓ Total statutes in database: {len(all_statutes)}")
        
        # Show statute types
        types = set(s['type'] for s in all_statutes)
        print(f"✓ Statute types: {', '.join(types)}")
        
        # Search by title
        results = db.search_by_title("Labour")
        print(f"✓ Search by title 'Labour': {len(results)} results")
        if results:
            print(f"  Found: {results[0].title}")
        
        # Search by keyword
        results = db.search_by_keyword("employment")
        print(f"✓ Search by keyword 'employment': {len(results)} results")
        
        # Get statute by ID
        labour_act = db.get_statute("LABOUR_ACT_2003")
        if labour_act:
            print(f"✓ Retrieved statute: {labour_act.title}")
            print(f"  Year enacted: {labour_act.year_enacted}")
            print(f"  Sections: {len(labour_act.sections)}")
            
            # Get specific section
            if labour_act.sections:
                first_section = list(labour_act.sections.items())[0]
                print(f"  Sample section: {first_section[0]}")
        
        # Search sections
        section_results = db.search_sections("employment")
        print(f"✓ Section search for 'employment': {len(section_results)} matches")
        
        print("✓ Statute Database: PASSED\n")
        return True
    
    except Exception as e:
        print(f"✗ Statute Database: FAILED - {str(e)}\n")
        return False


def test_module_integration():
    """Test integration between modules"""
    print("="*70)
    print("TEST 6: Module Integration")
    print("="*70)
    
    try:
        # Test that all modules can be imported together
        orchestrator = get_llm_orchestrator()
        generator = get_case_brief_generator()
        assistant = get_pleadings_assistant()
        simulator = get_strategy_simulator()
        statute_db = get_statute_database()
        
        print("✓ All Layer 3 modules imported successfully")
        
        # Test that they share state properly
        print(f"✓ LLM orchestrator has {len(orchestrator.available_providers())} providers")
        print(f"✓ Statute database has {len(statute_db.list_all_statutes())} statutes")
        print(f"✓ Strategy simulator ready with {len(simulator.precedent_analyzer.__class__.__dict__)} methods")
        
        # Test scenario using multiple modules
        scenario = LitigationScenario(
            name="Multi-module Test",
            client_position="plaintiff",
            key_facts=["Breach of labour contract"],
            legal_theories=["Breach of contract", "Wrongful dismissal"],
            opponent_strengths=[]
        )
        
        assessment = simulator.assess_strategy(scenario)
        print(f"✓ Multi-module strategy assessment: {assessment.overall_score:.1f}/100")
        
        print("✓ Module Integration: PASSED\n")
        return True
    
    except Exception as e:
        print(f"✗ Module Integration: FAILED - {str(e)}\n")
        return False


def test_data_models():
    """Test Pydantic data models"""
    print("="*70)
    print("TEST 7: Data Models")
    print("="*70)
    
    try:
        from api.models import (
            CaseBriefModel,
            PlaidingDraft,
            StrategyAnalysisResponse,
            StatuteInterpretationResponse
        )
        
        # Test CaseBriefModel
        brief_model = CaseBriefModel(
            case_id="GHASC/2023/001",
            case_name="Test v. Defendant",
            court="Ghana Supreme Court",
            judge="Anin-Yeboah JSC",
            facts="Test facts",
            issue="Test issue",
            holding="Test holding",
            reasoning="Test reasoning"
        )
        print(f"✓ CaseBriefModel created: {brief_model.case_name}")
        
        # Test PlaidingDraft
        pleading_model = PlaidingDraft(
            pleading_type="statement_of_claim",
            case_number="HC/2023/001",
            parties=["Plaintiff", "Defendant"],
            content="Test pleading content"
        )
        print(f"✓ PlaidingDraft created: {pleading_model.pleading_type}")
        
        # Test StrategyAnalysisResponse
        strategy_model = StrategyAnalysisResponse(
            strategy_name="Test Strategy",
            legal_strength=0.8,
            factual_strength=0.75,
            overall_score=78.5,
            predicted_outcome="plaintiff_win",
            outcome_probability=0.75,
            estimated_timeline_days=365,
            estimated_cost=25000.0,
            recommendations=["Recommendation 1", "Recommendation 2"]
        )
        print(f"✓ StrategyAnalysisResponse created: {strategy_model.strategy_name}")
        
        # Test StatuteInterpretationResponse
        statute_model = StatuteInterpretationResponse(
            statute_id="LABOUR_ACT_2003",
            statute_title="Labour Act, 2003",
            section_number="15",
            section_text="Termination of employment",
            statute_type="act",
            year_enacted=2003
        )
        print(f"✓ StatuteInterpretationResponse created: {statute_model.statute_title}")
        
        print("✓ Data Models: PASSED\n")
        return True
    
    except Exception as e:
        print(f"✗ Data Models: FAILED - {str(e)}\n")
        return False


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("GLIS LAYER 3 INTEGRATION TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("LLM Integration", test_llm_integration),
        ("Case Brief Generator", test_case_brief_generator),
        ("Pleadings Assistant", test_pleadings_assistant),
        ("Strategy Simulator", test_strategy_simulator),
        ("Statute Database", test_statute_database),
        ("Module Integration", test_module_integration),
        ("Data Models", test_data_models),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {str(e)}\n")
            results.append(False)
    
    # Print summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✓ PASSED" if results[i] else "✗ FAILED"
        print(f"{status:12} - {test_name}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
    print(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
