"""
Pydantic models for case data validation and API serialization
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import re


class CourtCase(BaseModel):
    """Main case model with validation"""
    case_id: str = Field(..., description="Unique case ID e.g., GHASC/2023/45")
    source_url: str = Field(..., description="Full URL to judgment")
    case_name: str = Field(..., description="Case title e.g., ADJEI vs. MENSAH")
    neutral_citation: str = Field(..., description="Neutral citation [YYYY] GHASC Number")
    date_decided: str = Field(..., description="ISO format date YYYY-MM-DD")
    coram: List[str] = Field(..., description="List of judges")
    court: str = Field(default="Supreme Court of Ghana")
    case_summary: str = Field(..., description="First 200 characters of judgment")
    full_text: str = Field(..., description="Complete judgment text")
    legal_issues: List[str] = Field(default_factory=list, description="Detected legal topics")
    referenced_statutes: List[str] = Field(default_factory=list, description="Laws cited")
    cited_cases: List[str] = Field(default_factory=list, description="Previous cases cited")
    disposition: str = Field(..., description="Appeal decision")
    data_quality_score: int = Field(ge=0, le=100, description="Quality score 0-100")
    last_updated: str = Field(..., description="ISO timestamp of collection")

    @validator('case_id')
    def validate_case_id(cls, v):
        """Validate case ID format: GHASC/YYYY/Number"""
        if not re.match(r'^GHASC/\d{4}/\d+$', v):
            raise ValueError('Invalid case ID format. Expected: GHASC/YYYY/Number')
        return v

    @validator('neutral_citation')
    def validate_citation(cls, v):
        """Validate neutral citation format: [YYYY] GHASC Number"""
        if not re.match(r'^\[\d{4}\] GHASC \d+$', v):
            raise ValueError('Invalid citation format. Expected: [YYYY] GHASC Number')
        return v

    @validator('date_decided')
    def validate_date(cls, v):
        """Validate ISO date format"""
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError('Invalid date format. Expected: YYYY-MM-DD')
        return v

    @validator('coram')
    def validate_judges(cls, v):
        """Ensure at least 3 judges for Supreme Court"""
        if len(v) < 3:
            raise ValueError('Supreme Court cases must have at least 3 judges')
        return v

    @validator('full_text')
    def validate_text_length(cls, v):
        """Ensure text is substantial"""
        if len(v) < 500:
            raise ValueError('Full text must be at least 500 characters')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "GHASC/2023/45",
                "source_url": "https://ghalii.org/judgment/ghasc/2023/45",
                "case_name": "ADJEI VS. MENSAH",
                "neutral_citation": "[2023] GHASC 45",
                "date_decided": "2023-06-15",
                "coram": ["Dotse JSC", "Pwamang JSC", "Kulendi JSC"],
                "court": "Supreme Court of Ghana",
                "case_summary": "This case concerns the interpretation of property rights...",
                "full_text": "The full judgment text...",
                "legal_issues": ["property rights", "succession"],
                "referenced_statutes": ["Act 29", "1992 Constitution"],
                "cited_cases": ["Mensah v. Kusi [2000] GHASC 1"],
                "disposition": "Appeal allowed",
                "data_quality_score": 95,
                "last_updated": "2024-01-06T10:30:00Z"
            }
        }


class CaseMetadata(BaseModel):
    """Metadata for entire database"""
    total_cases: int = 0
    last_updated: str = Field(..., description="ISO timestamp")
    coverage: str = "2000-2024"
    data_quality_average: float = 0.0
    version: str = "1.0.0"


class CaseIndex(BaseModel):
    """Index structures for fast search"""
    by_year: Dict[str, List[str]] = Field(default_factory=dict)
    by_judge: Dict[str, List[str]] = Field(default_factory=dict)
    by_statute: Dict[str, List[str]] = Field(default_factory=dict)
    by_legal_issue: Dict[str, List[str]] = Field(default_factory=dict)


class CaseDatabase(BaseModel):
    """Complete case database structure"""
    metadata: CaseMetadata
    cases: List[CourtCase] = Field(default_factory=list)
    indexes: CaseIndex = Field(default_factory=CaseIndex)


class SearchQuery(BaseModel):
    """Search query model for API"""
    q: Optional[str] = Field(None, description="Search text")
    year_from: Optional[int] = Field(None, ge=2000, le=2024)
    year_to: Optional[int] = Field(None, ge=2000, le=2024)
    judge: Optional[str] = None
    statute: Optional[str] = None
    legal_issue: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SearchResult(BaseModel):
    """Search result item"""
    case_id: str
    case_name: str
    neutral_citation: str
    date_decided: str
    relevance_score: float = Field(ge=0, le=1)
    snippet: str


class SearchResponse(BaseModel):
    """Search API response"""
    total: int
    results: List[SearchResult]
    query: SearchQuery


class QualityReport(BaseModel):
    """Data quality assessment"""
    total_cases: int
    average_quality_score: float
    cases_by_score: Dict[str, int]  # e.g., {"100": 50, "80-99": 150}
    missing_fields: Dict[str, int]  # e.g., {"judges": 5, "date": 3}
    validation_issues: List[str]
    timestamp: str


class DailyStats(BaseModel):
    """Daily progress report"""
    date: str
    target: int = 500
    scraped_today: int = 0
    total_scraped: int = 0
    success_rate: float = 0.0
    average_quality_score: float = 0.0
    errors_encountered: int = 0
    estimated_completion: str = ""


class ErrorLog(BaseModel):
    """Error entry in logs"""
    timestamp: str
    url: str
    error_type: str
    message: str
    retry_count: int = 0


# ============= LAYER 2: INTELLIGENCE MODELS =============

class LegalConceptInfo(BaseModel):
    """Extracted legal concept"""
    concept_id: str
    concept_name: str
    confidence: float = Field(ge=0, le=1)
    occurrences: int
    definition: Optional[str] = None
    related_statutes: List[str] = Field(default_factory=list)


class CitationRelationshipModel(BaseModel):
    """Citation relationship between cases"""
    citing_case: str
    cited_case: str
    relationship_type: str  # "followed", "affirmed", "overruled", "distinguished"
    context: str


class CaseAuthorityModel(BaseModel):
    """Authority status of a case"""
    case_id: str
    status: str  # "good law", "overruled", "reversed", "bad law"
    authority_score: float = Field(ge=0, le=100)
    is_good_law: bool
    is_overruled: bool
    overruling_cases: List[str] = Field(default_factory=list)
    affirming_cases: List[str] = Field(default_factory=list)
    total_citations: int
    red_flag: bool
    green_flag: bool


class ConceptSearchResponse(BaseModel):
    """Response from concept-based search"""
    concept: str
    matching_cases: List[SearchResult]
    related_concepts: List[LegalConceptInfo] = Field(default_factory=list)
    total_found: int


class SemanticSearchResponse(BaseModel):
    """Response from semantic similarity search"""
    query: str
    semantic_results: List[SearchResult]
    similar_cases: List[SearchResult] = Field(default_factory=list)
    total_found: int


# ============= LAYER 3: REASONING MODELS =============

class PrecedentCaseInfo(BaseModel):
    """Information about a precedent case"""
    case_id: str
    case_name: str
    date_decided: str
    holding: str
    status: str  # "good law", "overruled", etc.
    key_extract: Optional[str] = None


class EvolutionStep(BaseModel):
    """Step in legal principle evolution"""
    year: str
    case: str
    case_id: str
    holding: str
    judges: List[str]
    relationship_to_prior: Optional[str] = None


class PrecedentAnalysisResponse(BaseModel):
    """Response from precedent analyzer"""
    concept: str
    total_precedents: int
    date_range: str
    initial_case: PrecedentCaseInfo
    evolution_timeline: List[EvolutionStep]
    current_state: str
    conflicts_found: List[Dict] = Field(default_factory=list)
    analysis_summary: str


class CaseBriefModel(BaseModel):
    """Structured case brief"""
    case_id: str
    case_name: str
    neutral_citation: str
    facts: str
    legal_issues: List[str]
    holding: str
    ratio_decidendi: str
    obiter_dicta: Optional[str] = None
    judges: List[str]
    date_decided: str


class PlaidingDraftRequest(BaseModel):
    """Request for pleading draft"""
    pleading_type: str  # "statement_of_claim", "defense", "counterclaim"
    parties: Dict[str, str]  # {"plaintiff": "John Adjei", "defendant": "Kwasi Mensah"}
    facts: str
    causes_of_action: List[str]
    relevant_precedents: List[str] = Field(default_factory=list)
    relief_sought: str


class PlaidingDraft(BaseModel):
    """Generated pleading document"""
    pleading_type: str
    draft_content: str
    cited_precedents: List[str]
    suggested_statutes: List[str]
    draft_format: str = "markdown"  # Can be converted to docx


class StrategyAnalysisResponse(BaseModel):
    """Litigation strategy analysis"""
    scenario: str  # Description of facts
    possible_causes_of_action: List[Dict] = Field(
        description="List with cause, strength (%), supporting precedents"
    )
    recommended_strategy: str
    risk_assessment: Dict
    procedural_considerations: List[str]
    jurisdictional_issues: List[str]


class CitatorAlertModel(BaseModel):
    """Alert about case status change"""
    alert_id: str
    case_id: str
    case_name: str
    alert_type: str  # "overruled", "affirmed", "new_citation"
    date_created: str
    description: str
    severity: str  # "high", "medium", "low"


class StatuteInterpretationResponse(BaseModel):
    """Response from statutory interpreter"""
    statute: str
    section: Optional[str] = None
    statutory_text: str
    judicial_interpretation: str
    key_cases: List[PrecedentCaseInfo] = Field(default_factory=list)
    amendments: List[Dict] = Field(default_factory=list)
    ghanaian_application: str
