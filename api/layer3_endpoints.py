"""
Layer 3 Reasoning Endpoints - Advanced Legal Intelligence

Provides REST API access to:
- Case brief generation
- Pleadings assistant
- Strategy simulator
- Statute interpretation
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from reasoning.case_brief_generator import get_case_brief_generator, CaseBrief
from reasoning.pleadings_assistant import (
    get_pleadings_assistant,
    PleadingType,
    CourtType,
    Party,
    PleadingMetadata,
)
from reasoning.strategy_simulator import (
    get_strategy_simulator,
    LitigationScenario,
)
from intelligence.statute_db import (
    get_statute_database,
    StatuteType,
)
from reasoning.llm_integration import (
    get_llm_orchestrator,
    ModelProvider,
)
from api.models import (
    CaseBriefModel,
    PlaidingDraftRequest,
    PlaidingDraft,
    StrategyAnalysisResponse,
    StatuteInterpretationResponse,
)

# Initialize routers
router = APIRouter(prefix="/v3", tags=["Layer 3 - Reasoning & Advanced Intelligence"])

# Initialize modules
brief_generator = get_case_brief_generator()
pleadings_assistant = get_pleadings_assistant()
strategy_simulator = get_strategy_simulator()
statute_db = get_statute_database()
llm_orchestrator = get_llm_orchestrator()


# ==============================================================================
# Case Brief Generation Endpoints
# ==============================================================================

@router.post("/brief/generate")
async def generate_case_brief(
    case_id: str = Query(..., description="Case identifier (e.g., GHASC/2023/001)"),
    case_name: str = Query(..., description="Name of the case"),
    case_text: str = Query(..., description="Full text of the case judgment"),
    court: str = Query("Ghana Supreme Court", description="Court name"),
    judge: Optional[str] = Query(None, description="Judge name"),
) -> CaseBriefModel:
    """
    Generate a structured case brief using LLM analysis.
    
    Returns Facts, Issue, Holding, and Reasoning sections.
    """
    try:
        metadata = {
            'court': court,
            'year': int(case_id.split('/')[-2]) if '/' in case_id else datetime.now().year,
            'date_decided': datetime.now().isoformat(),
            'judge': judge or ''
        }
        
        brief = brief_generator.generate_brief(
            case_id=case_id,
            case_name=case_name,
            case_text=case_text,
            metadata=metadata
        )
        
        return CaseBriefModel(
            case_id=brief.case_id,
            case_name=brief.case_name,
            court=brief.court,
            judge=brief.judge,
            facts=brief.facts.content,
            issue=brief.issue.content,
            holding=brief.holding.content,
            reasoning=brief.reasoning.content,
            key_concepts=brief.key_concepts,
            total_cost=brief.total_cost_usd
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brief generation failed: {str(e)}")


@router.get("/brief/compare")
async def compare_briefs(
    case_ids: List[str] = Query(..., description="List of case IDs to compare"),
) -> Dict[str, Any]:
    """
    Compare multiple case briefs and identify similarities and differences.
    """
    try:
        if len(case_ids) < 2:
            raise ValueError("At least 2 cases required for comparison")
        
        # This would load actual briefs - placeholder for now
        return {
            "status": "comparison_generated",
            "cases_compared": case_ids,
            "similarities": ["Similar legal principle", "Similar factual pattern"],
            "differences": ["Different jurisdiction", "Different relief sought"],
            "key_distinctions": ["Case 1 involves X, Case 2 involves Y"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Comparison failed: {str(e)}")


# ==============================================================================
# Pleadings Assistant Endpoints
# ==============================================================================

@router.post("/pleading/generate/summons")
async def generate_summons(
    case_number: str = Query(..., description="Court case number"),
    plaintiff_name: str = Query(..., description="Plaintiff/Appellant name"),
    defendant_name: str = Query(..., description="Defendant/Respondent name"),
    court_type: str = Query("high_court", description="Type of court"),
) -> PlaidingDraft:
    """
    Generate a legal summons document.
    """
    try:
        court = CourtType[court_type.upper().replace('-', '_')]
        
        metadata = PleadingMetadata(
            case_name=f"{plaintiff_name} v. {defendant_name}",
            case_number=case_number,
            court=court,
            filing_date=datetime.now().isoformat().split('T')[0],
            plaintiff=Party(name=plaintiff_name, capacity="Plaintiff", address=""),
            defendant=Party(name=defendant_name, capacity="Defendant", address="")
        )
        
        pleading = pleadings_assistant.generate_summons(
            metadata=metadata,
            relief=["Such other relief as the court shall deem fit"]
        )
        
        return PlaidingDraft(
            pleading_type=pleading.pleading_type.value,
            case_number=case_number,
            parties=[plaintiff_name, defendant_name],
            content=pleading.to_text(),
            generated_date=pleading.generated_date
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summons generation failed: {str(e)}")


@router.post("/pleading/generate/statement-of-claim")
async def generate_statement_of_claim(
    request: PlaidingDraftRequest,
) -> PlaidingDraft:
    """
    Generate a Statement of Claim with facts and legal basis.
    """
    try:
        court = CourtType[request.court_type.upper().replace('-', '_')]
        
        metadata = PleadingMetadata(
            case_name=f"{request.plaintiff} v. {request.defendant}",
            case_number=request.case_number,
            court=court,
            filing_date=datetime.now().isoformat().split('T')[0],
            plaintiff=Party(name=request.plaintiff, capacity="Plaintiff", address=request.plaintiff_address or ""),
            defendant=Party(name=request.defendant, capacity="Defendant", address=request.defendant_address or "")
        )
        
        pleading = pleadings_assistant.generate_statement_of_claim(
            metadata=metadata,
            facts=request.facts or [],
            legal_basis=request.legal_basis or [],
            relief=request.relief_sought or []
        )
        
        return PlaidingDraft(
            pleading_type=pleading.pleading_type.value,
            case_number=request.case_number,
            parties=[request.plaintiff, request.defendant],
            content=pleading.to_text(),
            citations_used=len(pleading.citations),
            generated_date=pleading.generated_date
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statement of Claim generation failed: {str(e)}")


@router.post("/pleading/generate/defence")
async def generate_defence(
    case_number: str = Query(...),
    defendant_name: str = Query(...),
    plaintiff_name: str = Query(...),
    admissions: List[str] = Query([]),
    denials: List[str] = Query([]),
    specific_defences: List[str] = Query([]),
    court_type: str = Query("high_court"),
) -> PlaidingDraft:
    """
    Generate a Defence to a Statement of Claim.
    """
    try:
        court = CourtType[court_type.upper().replace('-', '_')]
        
        metadata = PleadingMetadata(
            case_name=f"{plaintiff_name} v. {defendant_name}",
            case_number=case_number,
            court=court,
            filing_date=datetime.now().isoformat().split('T')[0],
            plaintiff=Party(name=plaintiff_name, capacity="Plaintiff", address=""),
            defendant=Party(name=defendant_name, capacity="Defendant", address="")
        )
        
        pleading = pleadings_assistant.generate_defence(
            metadata=metadata,
            admissions=admissions,
            denials=denials,
            specific_defences=specific_defences
        )
        
        return PlaidingDraft(
            pleading_type=pleading.pleading_type.value,
            case_number=case_number,
            parties=[plaintiff_name, defendant_name],
            content=pleading.to_text(),
            generated_date=pleading.generated_date
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Defence generation failed: {str(e)}")


# ==============================================================================
# Strategy Simulator Endpoints
# ==============================================================================

@router.post("/strategy/analyze")
async def analyze_litigation_strategy(
    client_position: str = Query(..., description="'plaintiff' or 'defendant'"),
    legal_theories: List[str] = Query(..., description="Legal theories to pursue"),
    key_facts: List[str] = Query(..., description="Key facts supporting position"),
    opponent_strengths: List[str] = Query([], description="Opponent's strong points"),
    opponent_weaknesses: List[str] = Query([], description="Opponent's weak points"),
    budget: float = Query(50000.0, description="Available litigation budget in GHS"),
) -> StrategyAnalysisResponse:
    """
    Analyze litigation strategy and predict outcomes with risk assessment.
    
    Returns:
    - Outcome probability
    - Risk assessment
    - Cost estimation
    - Strategic recommendations
    """
    try:
        if client_position not in ['plaintiff', 'defendant']:
            raise ValueError("client_position must be 'plaintiff' or 'defendant'")
        
        scenario = LitigationScenario(
            name=f"{client_position.title()} Strategy",
            client_position=client_position,
            key_facts=key_facts,
            legal_theories=legal_theories,
            opponent_strengths=opponent_strengths,
            opponent_weaknesses=opponent_weaknesses
        )
        
        assessment = strategy_simulator.assess_strategy(scenario, budget=budget)
        
        return StrategyAnalysisResponse(
            strategy_name=assessment.strategy_name,
            legal_strength=round(assessment.legal_strength, 2),
            factual_strength=round(assessment.factual_strength, 2),
            overall_score=round(assessment.overall_score, 1),
            predicted_outcome=assessment.predicted_outcome.primary_outcome.value,
            outcome_probability=round(assessment.predicted_outcome.outcome_probability, 2),
            estimated_timeline_days=assessment.predicted_outcome.timeline_estimate,
            estimated_cost=round(assessment.cost_estimate.total_cost, 2),
            risks=assessment.risk_assessment.get('risk_factors', [])[:3],
            recommendations=assessment.recommendations[:5]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy analysis failed: {str(e)}")


@router.post("/strategy/compare")
async def compare_strategies(
    scenarios: List[Dict[str, Any]] = Query(..., description="List of scenario objects"),
    budget: float = Query(50000.0),
) -> List[StrategyAnalysisResponse]:
    """
    Compare multiple litigation strategies and rank by viability.
    """
    try:
        # Parse scenarios
        scenario_objects = [
            LitigationScenario(
                name=s.get('name', 'Strategy'),
                client_position=s.get('client_position', 'plaintiff'),
                key_facts=s.get('key_facts', []),
                legal_theories=s.get('legal_theories', []),
                opponent_strengths=s.get('opponent_strengths', []),
                opponent_weaknesses=s.get('opponent_weaknesses', [])
            )
            for s in scenarios
        ]
        
        assessments = strategy_simulator.compare_strategies(scenario_objects, budget=budget)
        
        return [
            StrategyAnalysisResponse(
                strategy_name=a.strategy_name,
                legal_strength=round(a.legal_strength, 2),
                factual_strength=round(a.factual_strength, 2),
                overall_score=round(a.overall_score, 1),
                predicted_outcome=a.predicted_outcome.primary_outcome.value,
                outcome_probability=round(a.predicted_outcome.outcome_probability, 2),
                recommendations=a.recommendations[:3]
            )
            for a in assessments
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy comparison failed: {str(e)}")


# ==============================================================================
# Statute Interpretation Endpoints
# ==============================================================================

@router.get("/statute/search")
async def search_statutes(
    query: str = Query(..., description="Search query (title, keyword, or section)"),
    statute_type: Optional[str] = Query(None, description="Filter by statute type"),
) -> List[Dict[str, Any]]:
    """
    Search Ghana statutes and legislation.
    """
    try:
        # Search by title
        by_title = statute_db.search_by_title(query)
        
        # Search by keyword
        by_keyword = statute_db.search_by_keyword(query)
        
        # Search sections
        by_section = statute_db.search_sections(query)
        
        results = []
        
        # Add statute results
        for statute in by_title + by_keyword:
            result = {
                'type': 'statute',
                'statute_id': statute.statute_id,
                'title': statute.title,
                'short_title': statute.short_title,
                'statute_type': statute.statute_type.value,
                'year_enacted': statute.year_enacted,
                'is_current': statute.is_current,
            }
            if result not in results:
                results.append(result)
        
        # Add section results
        for statute_id, section_num, section_text in by_section:
            results.append({
                'type': 'section',
                'statute_id': statute_id,
                'section_number': section_num,
                'section_text': section_text[:200] + '...' if len(section_text) > 200 else section_text,
            })
        
        return results[:20]  # Limit to 20 results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statute search failed: {str(e)}")


@router.get("/statute/{statute_id}/section/{section_number}")
async def get_statute_section(
    statute_id: str = Query(...),
    section_number: str = Query(...),
) -> StatuteInterpretationResponse:
    """
    Retrieve specific statute section with interpretation guidance.
    """
    try:
        result = statute_db.interpret_statute(statute_id, section_number)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Statute {statute_id} section {section_number} not found")
        
        return StatuteInterpretationResponse(
            statute_id=result['statute_id'],
            statute_title=result['statute_title'],
            section_number=result['section_number'],
            section_text=result['section_text'],
            statute_type=result['statute_type'],
            year_enacted=result['year_enacted'],
            interpretation="Consult legal expert for specific interpretation",
            related_sections=[],
            case_law_citations=[]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Section retrieval failed: {str(e)}")


@router.get("/statutes/list")
async def list_all_statutes(
    statute_type: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """
    List all available Ghana statutes.
    """
    try:
        all_statutes = statute_db.list_all_statutes()
        
        if statute_type:
            all_statutes = [s for s in all_statutes if s['type'] == statute_type]
        
        return sorted(all_statutes, key=lambda x: x['year_enacted'], reverse=True)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statute listing failed: {str(e)}")


# ==============================================================================
# LLM Management Endpoints
# ==============================================================================

@router.get("/llm/providers")
async def get_available_llm_providers() -> Dict[str, List[str]]:
    """
    Get list of available LLM providers and models.
    """
    try:
        providers = llm_orchestrator.available_providers()
        provider_names = [p.value for p in providers]
        
        return {
            "available_models": provider_names,
            "primary_model": llm_orchestrator.config.primary_provider.value,
            "fallback_models": [p.value for p in llm_orchestrator.config.fallback_providers]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get providers: {str(e)}")


@router.get("/llm/costs")
async def get_llm_costs() -> Dict[str, Any]:
    """
    Get LLM API usage and cost summary.
    """
    try:
        summary = llm_orchestrator.get_cost_summary()
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost summary: {str(e)}")


@router.post("/llm/model/set")
async def set_primary_llm_model(
    model: str = Query(..., description="Model name (e.g., gpt-4, gpt-3.5-turbo)"),
) -> Dict[str, str]:
    """
    Change the primary LLM model.
    """
    try:
        # Map model string to ModelProvider enum
        model_map = {p.value: p for p in ModelProvider}
        
        if model not in model_map:
            raise ValueError(f"Unknown model: {model}. Available: {list(model_map.keys())}")
        
        llm_orchestrator.set_primary_provider(model_map[model])
        
        return {
            "status": "success",
            "primary_model": model,
            "message": f"Primary LLM model changed to {model}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==============================================================================
# Health Check
# ==============================================================================

@router.get("/health")
async def v3_health_check() -> Dict[str, str]:
    """
    Check Layer 3 reasoning system health.
    """
    return {
        "status": "healthy",
        "layer": "Layer 3 - Reasoning & Advanced Intelligence",
        "components": [
            "Case Brief Generator",
            "Pleadings Assistant",
            "Strategy Simulator",
            "Statute Database",
            "LLM Integration"
        ],
        "timestamp": datetime.now().isoformat()
    }
