"""
Precedent Analyzer - Layer 3 Reasoning Module

Finds and analyzes precedent cases related to legal concepts and issues.
Shows how legal principles evolved across cases with timeline, holdings, and impacts.

Features:
- Find all cases discussing a concept
- Show principle evolution over time
- Identify conflicting holdings
- Build precedent matrices
- Generate precedent analysis reports
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from intelligence.citation_network import get_citation_network, CitationRelationship
from intelligence.concept_extractor import get_concept_extractor
from utils.legal_taxonomy import get_taxonomy


@dataclass
class PrecedentCaseInfo:
    """Information about a precedent case"""
    case_id: str
    case_name: str
    date_decided: str
    court: str
    judges: List[str]
    holding: str
    key_extract: str
    status: str  # "good law", "overruled", etc.


@dataclass
class PrecedentTimeline:
    """Timeline showing evolution of a legal principle"""
    concept: str
    initial_case: PrecedentCaseInfo
    evolution_steps: List[Dict]  # Chronological development
    current_state: str  # Current understanding of principle
    conflicts: List[Dict]  # Conflicting decisions


@dataclass
class PrecedentMatrix:
    """Matrix for comparing precedents"""
    concept: str
    cases: List[PrecedentCaseInfo]
    holdings: Dict[str, str]  # case_id -> holding
    distinguishing_factors: List[str]
    common_themes: List[str]


class PrecedentAnalyzer:
    """
    Analyzes precedent cases related to specific legal concepts
    """

    def __init__(self):
        self.citation_network = get_citation_network()
        self.concept_extractor = get_concept_extractor()
        self.taxonomy = get_taxonomy()

    def find_precedent_cases(
        self,
        concept: str,
        case_database: List[Dict],
        min_year: int = 2000,
        max_year: int = 2024
    ) -> List[PrecedentCaseInfo]:
        """
        Find all cases discussing a specific legal concept
        
        Args:
            concept: Legal concept (e.g., "fiduciary duty", "breach of contract")
            case_database: List of case dictionaries from database
            min_year: Minimum year to include
            max_year: Maximum year to include
            
        Returns:
            List of precedent cases discussing the concept
        """
        relevant_cases = []
        
        # Find concept in taxonomy
        found_concept = self.taxonomy.find_concept_by_name(concept)
        if not found_concept:
            return []
        
        for case in case_database:
            # Check if case text contains concept
            case_text = case.get('full_text', '').lower()
            concept_lower = concept.lower()
            
            if concept_lower in case_text:
                # Extract year from case
                try:
                    case_year = int(case.get('date_decided', '')[:4])
                    if min_year <= case_year <= max_year:
                        relevant_cases.append(PrecedentCaseInfo(
                            case_id=case.get('case_id'),
                            case_name=case.get('case_name'),
                            date_decided=case.get('date_decided'),
                            court=case.get('court', 'Supreme Court'),
                            judges=case.get('judges', []),
                            holding=self._extract_holding(case.get('full_text', '')),
                            key_extract=self._extract_key_passage(case.get('full_text', ''), concept),
                            status=self._determine_case_status(case.get('case_id'))
                        ))
                except (ValueError, TypeError):
                    pass
        
        # Sort by date
        relevant_cases.sort(key=lambda x: x.date_decided, reverse=True)
        return relevant_cases

    def analyze_principle_evolution(
        self,
        concept: str,
        precedent_cases: List[PrecedentCaseInfo]
    ) -> PrecedentTimeline:
        """
        Analyze how a legal principle evolved across cases
        
        Args:
            concept: Legal concept
            precedent_cases: List of relevant precedent cases
            
        Returns:
            PrecedentTimeline showing evolution
        """
        # Sort by date ascending (oldest to newest)
        sorted_cases = sorted(precedent_cases, key=lambda x: x.date_decided)
        
        if not sorted_cases:
            return None
        
        evolution_steps = []
        for i, case in enumerate(sorted_cases):
            step = {
                "year": case.date_decided[:4],
                "case": case.case_name,
                "case_id": case.case_id,
                "holding": case.holding,
                "judges": case.judges,
            }
            
            if i > 0:
                prev_case = sorted_cases[i-1]
                # Determine relationship
                citing_rels = self.citation_network.find_cited_cases(case.case_id)
                if prev_case.case_id in citing_rels.get(CitationRelationship.AFFIRMED, []):
                    step["relationship_to_prior"] = "affirmed previous holding"
                elif prev_case.case_id in citing_rels.get(CitationRelationship.OVERRULED, []):
                    step["relationship_to_prior"] = "overruled/reversed previous holding"
                elif prev_case.case_id in citing_rels.get(CitationRelationship.DISTINGUISHED, []):
                    step["relationship_to_prior"] = "distinguished from previous case"
                else:
                    step["relationship_to_prior"] = "no direct relationship"
            
            evolution_steps.append(step)
        
        # Determine current state
        current_case = sorted_cases[-1]
        current_state = f"{concept} in Ghana law is established by {current_case.case_name} ({current_case.date_decided[:4]}). "
        current_state += f"Current status: {current_case.status}"
        
        # Find conflicts
        conflicts = self._find_conflicting_decisions(sorted_cases)
        
        return PrecedentTimeline(
            concept=concept,
            initial_case=sorted_cases[0],
            evolution_steps=evolution_steps,
            current_state=current_state,
            conflicts=conflicts
        )

    def create_precedent_matrix(
        self,
        concept: str,
        precedent_cases: List[PrecedentCaseInfo]
    ) -> PrecedentMatrix:
        """
        Create a comparison matrix of precedent cases
        
        Args:
            concept: Legal concept
            precedent_cases: List of relevant cases
            
        Returns:
            PrecedentMatrix for comparison
        """
        holdings = {}
        for case in precedent_cases:
            holdings[case.case_id] = case.holding
        
        # Extract distinguishing factors
        distinguishing_factors = self._extract_distinguishing_factors(precedent_cases)
        
        # Find common themes
        common_themes = self._find_common_themes(precedent_cases)
        
        return PrecedentMatrix(
            concept=concept,
            cases=precedent_cases,
            holdings=holdings,
            distinguishing_factors=distinguishing_factors,
            common_themes=common_themes
        )

    def generate_precedent_analysis_report(
        self,
        concept: str,
        case_database: List[Dict]
    ) -> Dict:
        """
        Generate comprehensive precedent analysis report
        
        Args:
            concept: Legal concept to analyze
            case_database: Full case database
            
        Returns:
            Comprehensive analysis report
        """
        precedent_cases = self.find_precedent_cases(concept, case_database)
        
        if not precedent_cases:
            return {"error": f"No precedents found for '{concept}'"}
        
        timeline = self.analyze_principle_evolution(concept, precedent_cases)
        matrix = self.create_precedent_matrix(concept, precedent_cases)
        
        return {
            "concept": concept,
            "total_precedents": len(precedent_cases),
            "date_range": f"{precedent_cases[-1].date_decided} to {precedent_cases[0].date_decided}",
            "timeline": {
                "initial_case": {
                    "name": timeline.initial_case.case_name,
                    "year": timeline.initial_case.date_decided[:4],
                },
                "evolution": timeline.evolution_steps,
                "current_state": timeline.current_state,
                "conflicts": timeline.conflicts,
            },
            "case_matrix": {
                "cases": [
                    {
                        "id": c.case_id,
                        "name": c.case_name,
                        "date": c.date_decided,
                        "status": c.status,
                    }
                    for c in matrix.cases
                ],
                "common_themes": matrix.common_themes,
                "distinguishing_factors": matrix.distinguishing_factors,
            },
            "analysis_summary": self._generate_summary(concept, precedent_cases, timeline),
        }

    def _extract_holding(self, text: str) -> str:
        """Extract main holding from judgment text"""
        # Look for conclusion section
        conclusion_markers = ["In the result", "In conclusion", "We hold", "We find"]
        for marker in conclusion_markers:
            if marker.lower() in text.lower():
                idx = text.lower().find(marker.lower())
                return text[idx:idx+300].strip()
        return text[:200].strip()

    def _extract_key_passage(self, text: str, concept: str) -> str:
        """Extract key passage discussing a concept"""
        concept_lower = concept.lower()
        idx = text.lower().find(concept_lower)
        if idx != -1:
            start = max(0, idx - 100)
            end = min(len(text), idx + 300)
            return text[start:end].strip()
        return ""

    def _determine_case_status(self, case_id: str) -> str:
        """Determine current status of a case"""
        try:
            status = self.citation_network.get_case_status(case_id)
            return status.current_status
        except:
            return "good law"

    def _find_conflicting_decisions(self, cases: List[PrecedentCaseInfo]) -> List[Dict]:
        """Find conflicting decisions in precedent"""
        conflicts = []
        
        # Compare holdings
        for i in range(len(cases) - 1):
            case1 = cases[i]
            case2 = cases[i + 1]
            
            # Simple conflict detection: if one was overruled
            if "not" in case2.holding.lower() and "not" not in case1.holding.lower():
                conflicts.append({
                    "between": f"{case1.case_name} and {case2.case_name}",
                    "type": "possible reversal",
                })
        
        return conflicts

    def _extract_distinguishing_factors(self, cases: List[PrecedentCaseInfo]) -> List[str]:
        """Extract factors that distinguish cases"""
        factors = set()
        
        # Extract unique elements from each case
        for case in cases:
            words = case.key_extract.split()
            # Get uncommon terms
            for word in words:
                if len(word) > 7 and word not in ["contract", "judgment", "plaintiff", "defendant"]:
                    factors.add(word)
        
        return list(factors)[:10]

    def _find_common_themes(self, cases: List[PrecedentCaseInfo]) -> List[str]:
        """Find common themes across cases"""
        themes = set()
        
        for case in cases:
            # Extract commonly used legal terms
            text = case.key_extract.lower()
            common_terms = [
                "duty", "liability", "damages", "breach", "contract",
                "property", "rights", "obligation", "party", "court",
                "principle", "law", "statute", "equity", "justice"
            ]
            for term in common_terms:
                if term in text:
                    themes.add(term)
        
        return list(themes)

    def _generate_summary(self, concept: str, cases: List[PrecedentCaseInfo], timeline: PrecedentTimeline) -> str:
        """Generate text summary of precedent analysis"""
        summary = f"Precedent Analysis for {concept}:\n\n"
        summary += f"Found {len(cases)} relevant precedent cases spanning {timeline.evolution_steps[0]['year']} to {timeline.evolution_steps[-1]['year']}.\n\n"
        
        good_law_count = len([c for c in cases if c.status == "good law"])
        overruled_count = len([c for c in cases if c.status == "overruled"])
        
        summary += f"Current Status: {good_law_count} cases establishing good law, {overruled_count} overruled.\n\n"
        summary += f"Latest Authority: {timeline.evolution_steps[-1]['case']} ({timeline.evolution_steps[-1]['year']}).\n\n"
        
        if timeline.conflicts:
            summary += f"Notable Conflicts: {len(timeline.conflicts)} conflicts identified.\n"
        
        return summary


# Global instance
_precedent_analyzer = None


def get_precedent_analyzer() -> PrecedentAnalyzer:
    """Get or create global precedent analyzer"""
    global _precedent_analyzer
    if _precedent_analyzer is None:
        _precedent_analyzer = PrecedentAnalyzer()
    return _precedent_analyzer
