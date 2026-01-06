"""
FastAPI application for Ghana Legal Scraper
Provides REST endpoints for case search and retrieval
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from api.models import (
    CourtCase, SearchQuery, SearchResult, SearchResponse,
    QualityReport
)
from api.search import CaseSearchEngine
from api.intelligence_endpoints import router as intelligence_router
from api.layer3_endpoints import router as layer3_router
from scraper.storage import CaseStorage
from config.settings import API_HOST, API_PORT, API_DEBUG, TARGET_CASES, MIN_AVERAGE_QUALITY


# Initialize FastAPI app
app = FastAPI(
    title="Ghana Legal Intelligence System (GLIS) API",
    description="REST API for searching Ghana Supreme Court cases and analyzing legal precedent",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Layer 2 & 3 endpoints
app.include_router(intelligence_router)
app.include_router(layer3_router)

# Initialize search engine and storage
search_engine = CaseSearchEngine()
storage = CaseStorage()


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Ghana Legal Intelligence System (GLIS) API",
        "version": "3.0.0",
        "status": "operational",
        "description": "Layer 1 (Data), Layer 2 (Intelligence), and Layer 3 (Reasoning) endpoints available",
        "layers": {
            "layer_1_legacy": "Original scraper API (deprecated - see /search endpoints)",
            "layer_2_intelligence": {
                "semantic_search": "/v2/semantic/search",
                "concept_search": "/v2/concept/search",
                "taxonomy": "/v2/taxonomy/concepts",
                "case_authority": "/v2/case/{case_id}/authority",
                "precedent_analyze": "/v2/precedent/analyze",
                "citator_alerts": "/v2/alerts"
            },
            "layer_3_reasoning": {
                "case_brief_generate": "/v3/brief/generate",
                "case_brief_compare": "/v3/brief/compare",
                "pleading_summons": "/v3/pleading/generate/summons",
                "pleading_statement_of_claim": "/v3/pleading/generate/statement-of-claim",
                "pleading_defence": "/v3/pleading/generate/defence",
                "strategy_analyze": "/v3/strategy/analyze",
                "strategy_compare": "/v3/strategy/compare",
                "statute_search": "/v3/statute/search",
                "statute_section": "/v3/statute/{statute_id}/section/{section_number}",
                "statutes_list": "/v3/statutes/list",
                "llm_providers": "/v3/llm/providers",
                "llm_costs": "/v3/llm/costs",
                "llm_model_set": "/v3/llm/model/set"
            }
        },
        "documentation": "/docs",
        "endpoints": {
            "search": "/search",
            "advanced_search": "/search/advanced",
            "citation_lookup": "/case/{citation}",
            "statistics": "/stats",
            "health": "/health",
            "v3_health": "/v3/health"
        }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        stats = search_engine.get_statistics()
        return {
            "status": "healthy",
            "database_cases": stats.get('total_cases', 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@app.get("/search", response_model=SearchResponse)
async def basic_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Basic full-text search across case names, summaries, and text.
    
    **Parameters:**
    - `q`: Search text (required)
    - `limit`: Number of results (1-100, default 10)
    - `offset`: Results offset for pagination
    """
    try:
        results = search_engine.basic_search(q, limit=limit, offset=offset)

        search_results = []
        for case in results:
            search_results.append(SearchResult(
                case_id=case.get('case_id', ''),
                case_name=case.get('case_name', ''),
                neutral_citation=case.get('neutral_citation', ''),
                date_decided=case.get('date_decided', ''),
                relevance_score=0.8,
                snippet=case.get('case_summary', '')[:150]
            ))

        return SearchResponse(
            total=len(results),
            results=search_results,
            query=SearchQuery(q=q, limit=limit, offset=offset)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/advanced", response_model=SearchResponse)
async def advanced_search(
    q: Optional[str] = Query(None, description="Full-text search"),
    year_from: Optional[int] = Query(None, ge=2000, le=2024),
    year_to: Optional[int] = Query(None, ge=2000, le=2024),
    judge: Optional[str] = Query(None, description="Judge name"),
    statute: Optional[str] = Query(None, description="Statute/Act name"),
    legal_issue: Optional[str] = Query(None, description="Legal issue"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Advanced search with multiple filters.
    
    **Parameters:**
    - `q`: Full-text search (optional)
    - `year_from`: Start year for date range
    - `year_to`: End year for date range
    - `judge`: Filter by judge name
    - `statute`: Filter by statute/act
    - `legal_issue`: Filter by legal issue
    - `limit`: Number of results
    - `offset`: Pagination offset
    """
    try:
        results = search_engine.advanced_search(
            query=q,
            year_from=year_from,
            year_to=year_to,
            judge=judge,
            statute=statute,
            legal_issue=legal_issue,
            limit=limit,
            offset=offset
        )

        search_results = []
        for case in results:
            search_results.append(SearchResult(
                case_id=case.get('case_id', ''),
                case_name=case.get('case_name', ''),
                neutral_citation=case.get('neutral_citation', ''),
                date_decided=case.get('date_decided', ''),
                relevance_score=0.85,
                snippet=case.get('case_summary', '')[:150]
            ))

        query_model = SearchQuery(
            q=q, year_from=year_from, year_to=year_to,
            judge=judge, statute=statute, legal_issue=legal_issue,
            limit=limit, offset=offset
        )

        return SearchResponse(
            total=len(results),
            results=search_results,
            query=query_model
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CASE RETRIEVAL ENDPOINTS
# ============================================================================

@app.get("/case/{case_id}")
async def get_case_by_id(case_id: str):
    """
    Retrieve complete case by Case ID (e.g., GHASC/2023/45)
    """
    try:
        case = storage.get_case_by_id(case_id)
        if not case:
            raise HTTPException(
                status_code=404,
                detail=f"Case {case_id} not found"
            )
        return case
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/citation/{citation}")
async def get_case_by_citation(citation: str):
    """
    Look up case by neutral citation (e.g., [2023] GHASC 45)
    """
    try:
        case = search_engine.citation_lookup(citation)
        if not case:
            raise HTTPException(
                status_code=404,
                detail=f"Case {citation} not found"
            )
        return case
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/year/{year}")
async def get_cases_by_year(year: int = Query(..., ge=2000, le=2024)):
    """
    Get all cases from a specific year
    """
    try:
        cases = search_engine.search_by_year(year)
        return {
            "year": year,
            "total": len(cases),
            "cases": cases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/judge/{judge_name}")
async def get_cases_by_judge(judge_name: str):
    """
    Get all cases where a specific judge participated
    """
    try:
        cases = search_engine.search_by_judge(judge_name)
        return {
            "judge": judge_name,
            "total": len(cases),
            "cases": cases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statute/{statute}")
async def get_cases_by_statute(statute: str):
    """
    Get all cases citing a specific statute
    """
    try:
        cases = search_engine.search_by_statute(statute)
        return {
            "statute": statute,
            "total": len(cases),
            "cases": cases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STATISTICS & METADATA ENDPOINTS
# ============================================================================

@app.get("/stats")
async def get_statistics():
    """
    Get comprehensive database statistics
    """
    try:
        stats = search_engine.get_statistics()
        db_stats = storage.get_stats()

        return {
            "database": stats,
            "scraping": db_stats,
            "mpp_status": {
                "target_cases": TARGET_CASES,
                "current_cases": stats.get('total_cases', 0),
                "target_met": stats.get('total_cases', 0) >= TARGET_CASES,
                "target_quality": MIN_AVERAGE_QUALITY,
                "current_quality": stats.get('average_quality', 0),
                "quality_met": stats.get('average_quality', 0) >= MIN_AVERAGE_QUALITY
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/quality-report")
async def get_quality_report() -> QualityReport:
    """
    Get data quality assessment report
    """
    try:
        cases = search_engine.cases_db.get('cases', [])

        if not cases:
            raise HTTPException(
                status_code=404,
                detail="No cases in database"
            )

        # Calculate quality metrics
        scores = [c.get('data_quality_score', 0) for c in cases]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Group scores
        score_groups = {
            "100": len([s for s in scores if s == 100]),
            "80-99": len([s for s in scores if 80 <= s < 100]),
            "60-79": len([s for s in scores if 60 <= s < 80]),
            "<60": len([s for s in scores if s < 60]),
        }

        # Count missing fields
        missing_fields = {}
        mandatory_fields = ['case_id', 'case_name', 'date_decided', 'coram', 'full_text']

        for field in mandatory_fields:
            missing = len([c for c in cases if not c.get(field)])
            if missing > 0:
                missing_fields[field] = missing

        return QualityReport(
            total_cases=len(cases),
            average_quality_score=round(avg_score, 2),
            cases_by_score=score_groups,
            missing_fields=missing_fields,
            validation_issues=[],
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.post("/admin/refresh-search-cache")
async def refresh_search_cache():
    """
    Refresh in-memory search cache from database file
    Admin endpoint for maintenance
    """
    try:
        search_engine.refresh_from_db()
        return {
            "status": "success",
            "message": "Search cache refreshed",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/database-info")
async def get_database_info():
    """
    Get low-level database information
    """
    try:
        import os
        from pathlib import Path
        from config.settings import DATABASE_PATH, CASES_JSON_PATH

        db_info = {
            "sqlite": {
                "path": str(DATABASE_PATH),
                "exists": DATABASE_PATH.exists(),
                "size_mb": os.path.getsize(DATABASE_PATH) / (1024 ** 2) if DATABASE_PATH.exists() else 0
            },
            "json": {
                "path": str(CASES_JSON_PATH),
                "exists": CASES_JSON_PATH.exists(),
                "size_mb": os.path.getsize(CASES_JSON_PATH) / (1024 ** 2) if CASES_JSON_PATH.exists() else 0
            }
        }

        return db_info

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        debug=API_DEBUG
    )
