"""
New Layer 2 & 3 API Endpoints for GLIS

Adds endpoints for:
- Semantic/concept-based search
- Precedent analysis
- Case authority & citator
- Case briefs
- Strategy analysis
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict
from api.models import (
    ConceptSearchResponse, SemanticSearchResponse, PrecedentAnalysisResponse,
    CaseAuthorityModel, CitatorAlertModel, CaseBriefModel, StrategyAnalysisResponse,
    StatuteInterpretationResponse, SearchResult, LegalConceptInfo
)
from intelligence import get_concept_extractor, get_citation_network
from reasoning import get_precedent_analyzer, get_citator
from utils.legal_taxonomy import get_taxonomy

# Initialize modules
router = APIRouter(prefix="/v2", tags=["Layer 2-3: Intelligence & Reasoning"])

# Global instances
concept_extractor = get_concept_extractor()
precedent_analyzer = get_precedent_analyzer()
citator = get_citator()
taxonomy = get_taxonomy()


# ============= LAYER 2: INTELLIGENCE ENDPOINTS =============

@router.get("/concept/search", response_model=ConceptSearchResponse)
async def concept_based_search(
    concept: str = Query(..., description="Legal concept to search for e.g., 'fiduciary duty'"),
    limit: int = Query(10, ge=1, le=50),
    case_data: Optional[List[Dict]] = None
):
    """
    Search for cases discussing a specific legal concept
    
    Uses semantic understanding to find related cases beyond keyword matching.
    
    Example: /concept/search?concept=fiduciary%20duty&limit=20
    """
    try:
        # Find concept in taxonomy
        found_concept = taxonomy.find_concept_by_name(concept)
        
        if not found_concept:
            raise HTTPException(
                status_code=404,
                detail=f"Concept '{concept}' not found in legal taxonomy"
            )
        
        # In real implementation, would search case database
        # This is a stub that shows the structure
        matching_cases = []
        related_concepts = [
            LegalConceptInfo(
                concept_id=found_concept.id,
                concept_name=found_concept.name,
                confidence=0.95,
                occurrences=5,
                definition=found_concept.definition,
                related_statutes=found_concept.statutes
            )
        ]
        
        return ConceptSearchResponse(
            concept=concept,
            matching_cases=matching_cases,
            related_concepts=related_concepts,
            total_found=len(matching_cases)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/semantic/search", response_model=SemanticSearchResponse)
async def semantic_search(
    query: str = Query(..., description="Natural language search query"),
    limit: int = Query(10, ge=1, le=50),
    threshold: float = Query(0.6, ge=0, le=1, description="Similarity threshold")
):
    """
    Search using semantic similarity and legal concept understanding
    
    Uses Legal-BERT embeddings to find cases with similar legal reasoning,
    even if they don't use the same keywords.
    
    Example: /semantic/search?query=when%20can%20a%20director%20be%20held%20liable
    """
    try:
        # Stub: In production, would use Legal-BERT embeddings
        return SemanticSearchResponse(
            query=query,
            semantic_results=[],
            similar_cases=[],
            total_found=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/taxonomy/concepts")
async def list_taxonomy_concepts(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search concepts")
):
    """
    Get all legal concepts in the taxonomy
    
    The taxonomy contains 100+ Ghanaian legal concepts hierarchically organized.
    
    Examples:
    - /taxonomy/concepts  (all)
    - /taxonomy/concepts?category=contract_law  (by category)
    - /taxonomy/concepts?search=fiduciary  (search)
    """
    try:
        if search:
            concepts = taxonomy.search_concepts(search)
        elif category:
            concepts = taxonomy.get_concepts_by_category(category)
        else:
            concepts = taxonomy.get_all_concepts()
        
        return {
            "count": len(concepts),
            "concepts": [
                {
                    "id": c.id,
                    "name": c.name,
                    "aliases": c.aliases,
                    "definition": c.definition,
                    "statutes": c.statutes,
                }
                for c in concepts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/taxonomy/categories")
async def list_taxonomy_categories():
    """Get all top-level legal categories in the taxonomy"""
    try:
        categories = taxonomy.get_categories()
        stats = taxonomy.get_taxonomy_stats()
        
        return {
            "categories": categories,
            "stats": stats,
            "concepts_per_category": {
                cat: len(taxonomy.get_concepts_by_category(cat))
                for cat in categories
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= LAYER 3: REASONING ENDPOINTS =============

@router.get("/precedent/analyze", response_model=PrecedentAnalysisResponse)
async def analyze_precedents(
    concept: str = Query(..., description="Legal concept to analyze"),
    year_from: int = Query(2000, ge=2000, le=2024),
    year_to: int = Query(2024, ge=2000, le=2024),
    case_database: Optional[List[Dict]] = None
):
    """
    Comprehensive precedent analysis for a legal concept
    
    Shows:
    - All cases discussing the concept
    - How the principle evolved over time
    - Current state of the law
    - Any conflicting decisions
    
    Example: /precedent/analyze?concept=breach%20of%20contract&year_from=2015
    """
    try:
        # Stub: would use case database
        case_database = case_database or []
        precedent_cases = precedent_analyzer.find_precedent_cases(
            concept, case_database, year_from, year_to
        )
        
        if not precedent_cases:
            raise HTTPException(
                status_code=404,
                detail=f"No precedents found for '{concept}' between {year_from}-{year_to}"
            )
        
        timeline = precedent_analyzer.analyze_principle_evolution(concept, precedent_cases)
        
        return PrecedentAnalysisResponse(
            concept=concept,
            total_precedents=len(precedent_cases),
            date_range=f"{year_from}-{year_to}",
            initial_case={
                "case_id": timeline.initial_case.case_id,
                "case_name": timeline.initial_case.case_name,
                "date_decided": timeline.initial_case.date_decided,
                "holding": timeline.initial_case.holding,
                "status": timeline.initial_case.status,
            },
            evolution_timeline=timeline.evolution_steps,
            current_state=timeline.current_state,
            conflicts_found=timeline.conflicts,
            analysis_summary=precedent_analyzer._generate_summary(concept, precedent_cases, timeline)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/case/{case_id}/authority", response_model=CaseAuthorityModel)
async def check_case_authority(case_id: str):
    """
    Check current authority status of a case
    
    Returns:
    - Current status (good law, overruled, reversed, etc.)
    - Authority score (0-100)
    - Red/green flags
    - Overruling and affirming cases
    
    Example: /case/GHASC%2F2023%2F45/authority
    """
    try:
        authority = citator.get_case_authority(case_id)
        
        return CaseAuthorityModel(
            case_id=authority.case_id,
            status=authority.status,
            authority_score=authority.authority_score,
            is_good_law=authority.is_good_law,
            is_overruled=authority.is_overruled,
            overruling_cases=authority.overruling_cases,
            affirming_cases=authority.affirming_cases,
            total_citations=authority.total_citations,
            red_flag=authority.red_flag,
            green_flag=authority.green_flag
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-citations")
async def validate_citations_before_use(
    cited_cases: List[str] = Query(..., description="Cases you want to cite")
):
    """
    Validate authority before citing cases
    
    Returns validation results with warnings if:
    - Case has been overruled
    - Case authority is questioned
    - Case has few supporting citations
    
    Useful for drafting pleadings or research notes.
    
    Example: /validate-citations?cited_cases=GHASC%2F2023%2F45&cited_cases=GHASC%2F2022%2F12
    """
    try:
        validation = citator.validate_authority_before_citing(
            cited_cases, "Current research"
        )
        
        return {
            "total_cases_checked": len(cited_cases),
            "safe_to_cite": sum(1 for v in validation.values() if v.get("can_cite", False)),
            "validation_results": validation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[CitatorAlertModel])
async def get_precedent_alerts(
    severity: Optional[str] = Query(None, description="Filter: high, medium, low"),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get alerts about changes in case authority
    
    Returns alerts when:
    - A case you depend on is overruled
    - Important case citations change
    - Precedent status updates
    
    Useful for legal monitoring and continuing education.
    """
    try:
        alerts = citator.get_alerts(severity)
        
        return [
            CitatorAlertModel(
                alert_id=a.alert_id,
                case_id=a.case_id,
                case_name=a.case_name,
                alert_type=a.alert_type,
                date_created=a.date_created,
                description=a.description,
                severity=a.severity
            )
            for a in alerts[:limit]
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/brief/generate", response_model=CaseBriefModel)
async def generate_case_brief(
    case_id: str = Query(..., description="Case to brief"),
    case_text: Optional[str] = Query(None, description="Full judgment text")
):
    """
    Generate structured case brief from judgment
    
    Automatically extracts:
    - Facts
    - Legal issues
    - Holding
    - Ratio decidendi
    - Obiter dicta
    
    Example: /brief/generate?case_id=GHASC%2F2023%2F45
    """
    try:
        # Stub: would use AI to generate brief
        return {
            "case_id": case_id,
            "case_name": "Case Name",
            "neutral_citation": "[2023] GHASC 45",
            "facts": "To be generated...",
            "legal_issues": [],
            "holding": "To be generated...",
            "ratio_decidendi": "To be generated...",
            "obiter_dicta": None,
            "judges": [],
            "date_decided": "2023-01-01"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/statute/interpret")
async def interpret_statute(
    statute: str = Query(..., description="Statute to interpret e.g., 'Act 29, Section 46'"),
    section: Optional[int] = Query(None)
):
    """
    Get judicial interpretation of statute provision
    
    Returns:
    - Statutory text
    - Key judicial interpretations
    - Relevant cases discussing this section
    - Amendment history
    - Application in Ghana
    
    Example: /statute/interpret?statute=Companies%20Act&section=179
    """
    try:
        # Stub: would query statute database and case interpretations
        return StatuteInterpretationResponse(
            statute=statute,
            section=section,
            statutory_text="To be retrieved...",
            judicial_interpretation="To be compiled...",
            key_cases=[],
            amendments=[],
            ghanaian_application="To be analyzed..."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy/analyze", response_model=StrategyAnalysisResponse)
async def analyze_litigation_strategy(
    scenario: str = Query(..., description="Describe your case facts"),
    jurisdiction: str = Query("High Court", description="Court jurisdiction")
):
    """
    Get litigation strategy analysis based on precedent
    
    Analyzes:
    - Possible causes of action with success probability
    - Recommended litigation strategy
    - Risk assessment
    - Procedural considerations
    - Jurisdictional issues
    
    Example: /strategy/analyze?scenario=My%20contractor%20breached%20the%20agreement
    """
    try:
        # Stub: would use AI + precedent analysis
        return StrategyAnalysisResponse(
            scenario=scenario,
            possible_causes_of_action=[],
            recommended_strategy="To be analyzed...",
            risk_assessment={},
            procedural_considerations=[],
            jurisdictional_issues=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intelligence/stats")
async def get_intelligence_stats():
    """Get statistics about the intelligence and reasoning layers"""
    try:
        taxonomy_stats = taxonomy.get_taxonomy_stats()
        citator_stats = citator.get_statistics()
        
        return {
            "taxonomy": taxonomy_stats,
            "citation_network": citator_stats.get("network_stats", {}),
            "alerts": {
                "total": citator_stats.get("total_alerts", 0),
                "high_severity": citator_stats.get("high_severity_alerts", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
