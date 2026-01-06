"""
Citation Network & Relationship Analysis Module

Builds a citation relationship graph to track how cases cite each other,
determine precedent status (overruled/affirmed/distinguished), and analyze
how legal principles evolve over time.

Features:
- Citation extraction from judgment text
- Case relationship mapping (cited → citing relationships)
- Precedent status tracking
- Citation history and evolution
- Authority assessment
"""

import re
import json
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum
from datetime import datetime


class CitationRelationship(Enum):
    """Types of citation relationships between cases"""
    FOLLOWED = "followed"
    AFFIRMED = "affirmed"
    REVERSED = "reversed"
    OVERRULED = "overruled"
    DISTINGUISHED = "distinguished"
    CITED = "cited"
    APPLIED = "applied"
    INTERPRETED = "interpreted"
    DISAGREED = "disagreed"


@dataclass
class CaseRelationship:
    """Relationship between two cases"""
    citing_case_id: str
    cited_case_id: str
    relationship_type: CitationRelationship
    context: str  # Surrounding text from judgment
    date_cited: str  # Date when citation occurred
    is_primary: bool = False  # Whether this is a main holding vs. passing reference


@dataclass
class CitationStatus:
    """Status of a case as it relates to precedent"""
    case_id: str
    current_status: str  # "good law", "overruled", "reversed", "distinguishable"
    is_overruled: bool
    overruling_cases: List[str]
    affirming_cases: List[str]
    distinguishing_cases: List[str]
    total_citations: int
    authority_score: float  # 0-100: higher = more authoritative


@dataclass
class PrecedentChain:
    """Shows evolution of legal principle across multiple cases"""
    concept: str
    initial_case: str
    cases_in_order: List[str]
    dates: List[str]
    key_holdings: List[str]
    modifications: List[str]


class GhanaCitationParser:
    """
    Parses citations in Ghana legal judgments
    Handles multiple citation formats and styles
    """

    # Ghana citation patterns
    GHANA_CITATION_PATTERNS = [
        # [2023] GHASC 12 (standard neutral citation)
        r'\[(\d{4})\]\s+GHASC\s+(\d+)',
        # [2023] GHASC 12 (with alternate spacing)
        r'\[(\d{4})\]\s*GHASC\s*(\d+)',
        # GHASC (2023) 12
        r'GHASC\s*\((\d{4})\)\s*(\d+)',
        # 2023 GHASC 12
        r'(\d{4})\s+GHASC\s+(\d+)',
        # Court of Appeal: [2023] GHCA 15
        r'\[(\d{4})\]\s+GHCA\s+(\d+)',
        # High Court: [2023] GHMC 5, [2023] GHLC 3
        r'\[(\d{4})\]\s+GH([MC|LC])\s+(\d+)',
    ]

    # Relationship indicators
    OVERRULED_PATTERNS = [
        r'overruled?\b',
        r'overturned?\b',
        r'set aside\b',
        r'quashed\b',
        r'reversed?\b',
    ]

    AFFIRMED_PATTERNS = [
        r'affirmed?\b',
        r'upheld?\b',
        r'confirmed?\b',
        r'approved?\b',
        r'endorsed?\b',
    ]

    DISTINGUISHED_PATTERNS = [
        r'distinguished\b',
        r'different from\b',
        r'not applicable\b',
        r'inapplicable\b',
    ]

    def __init__(self):
        self.compiled_citation_patterns = [re.compile(p, re.IGNORECASE) for p in self.GHANA_CITATION_PATTERNS]
        self.compiled_overruled = [re.compile(p, re.IGNORECASE) for p in self.OVERRULED_PATTERNS]
        self.compiled_affirmed = [re.compile(p, re.IGNORECASE) for p in self.AFFIRMED_PATTERNS]
        self.compiled_distinguished = [re.compile(p, re.IGNORECASE) for p in self.DISTINGUISHED_PATTERNS]

    def extract_citations(self, text: str) -> List[str]:
        """
        Extract all case citations from judgment text
        
        Args:
            text: Judgment text
            
        Returns:
            List of case identifiers in normalized format
        """
        citations = set()
        
        for pattern in self.compiled_citation_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                # Normalize to [YYYY] COURT Number format
                if len(match.groups()) >= 2:
                    year = match.group(1)
                    court_code = "GHASC"  # Default
                    case_number = match.group(2) if len(match.groups()) == 2 else match.group(3)
                    
                    citation = f"[{year}] {court_code} {case_number}"
                    citations.add(citation)
        
        return sorted(list(citations))

    def detect_relationship(self, text: str, citation: str) -> Optional[CitationRelationship]:
        """
        Detect relationship between current case and cited case
        
        Args:
            text: Context text around citation
            citation: Citation being analyzed
            
        Returns:
            CitationRelationship or None if relationship unclear
        """
        text_lower = text.lower()
        
        # Check for relationship indicators
        if any(pattern.search(text_lower) for pattern in self.compiled_overruled):
            return CitationRelationship.OVERRULED
        
        if any(pattern.search(text_lower) for pattern in self.compiled_affirmed):
            return CitationRelationship.AFFIRMED
        
        if any(pattern.search(text_lower) for pattern in self.compiled_distinguished):
            return CitationRelationship.DISTINGUISHED
        
        # Default to CITED if relationship unclear
        return CitationRelationship.CITED

    def extract_citation_context(self, text: str, citation: str, context_chars: int = 300) -> str:
        """
        Extract surrounding text context for a citation
        
        Args:
            text: Full judgment text
            citation: Citation to find
            context_chars: Characters before/after to include
            
        Returns:
            Context text
        """
        idx = text.find(citation)
        if idx == -1:
            return ""
        
        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(citation) + context_chars)
        return text[start:end].strip()


class CitationNetworkGraph:
    """
    Manages the citation relationship network
    """

    def __init__(self):
        self.relationships: List[CaseRelationship] = []
        self.case_status: Dict[str, CitationStatus] = {}
        self.citation_graph: Dict[str, List[Tuple[str, CitationRelationship]]] = defaultdict(list)
        self.reverse_citations: Dict[str, List[Tuple[str, CitationRelationship]]] = defaultdict(list)
        self.parser = GhanaCitationParser()

    def add_case_citations(
        self,
        case_id: str,
        full_text: str,
        date_decided: str
    ):
        """
        Parse case text and add all citations to network
        
        Args:
            case_id: The case that is citing
            full_text: Full judgment text
            date_decided: Date case was decided
        """
        citations = self.parser.extract_citations(full_text)
        
        for citation in citations:
            # Extract relationship context
            context = self.parser.extract_citation_context(full_text, citation)
            relationship = self.parser.detect_relationship(context, citation)
            
            if relationship:
                rel = CaseRelationship(
                    citing_case_id=case_id,
                    cited_case_id=citation,
                    relationship_type=relationship,
                    context=context,
                    date_cited=date_decided,
                    is_primary=(relationship != CitationRelationship.CITED)
                )
                
                self.relationships.append(rel)
                self.citation_graph[case_id].append((citation, relationship))
                self.reverse_citations[citation].append((case_id, relationship))

    def get_case_status(self, case_id: str) -> CitationStatus:
        """
        Determine current status of a case based on citation relationships
        
        Args:
            case_id: Case to analyze
            
        Returns:
            CitationStatus with current authority status
        """
        if case_id in self.case_status:
            return self.case_status[case_id]
        
        # Count relationship types
        overruling = []
        affirming = []
        distinguishing = []
        total = 0
        
        for citing_case, rel_type in self.reverse_citations[case_id]:
            if rel_type == CitationRelationship.OVERRULED:
                overruling.append(citing_case)
            elif rel_type == CitationRelationship.AFFIRMED:
                affirming.append(citing_case)
            elif rel_type == CitationRelationship.DISTINGUISHED:
                distinguishing.append(citing_case)
            total += 1
        
        # Determine current status
        if overruling:
            status = "overruled"
            is_overruled = True
        elif affirming or (total > 0 and not overruling):
            status = "good law"
            is_overruled = False
        else:
            status = "unknown"
            is_overruled = False
        
        # Calculate authority score (0-100)
        # Based on: affirming citations (positive), overruling (negative), age
        authority_score = 50.0  # Base score
        authority_score += len(affirming) * 5  # +5 per affirmation
        authority_score -= len(overruling) * 50  # -50 per overruling
        authority_score = max(0, min(100, authority_score))
        
        result = CitationStatus(
            case_id=case_id,
            current_status=status,
            is_overruled=is_overruled,
            overruling_cases=overruling,
            affirming_cases=affirming,
            distinguishing_cases=distinguishing,
            total_citations=total,
            authority_score=authority_score
        )
        
        self.case_status[case_id] = result
        return result

    def get_precedent_chain(
        self,
        concept: str,
        starting_case: str,
        max_depth: int = 5
    ) -> Optional[PrecedentChain]:
        """
        Trace how a legal concept evolved across multiple cases
        
        Args:
            concept: Legal concept to trace (e.g., "fiduciary duty")
            starting_case: Starting case ID
            max_depth: Maximum cases to follow
            
        Returns:
            PrecedentChain showing evolution
        """
        # Simplified: would require linking cases to concepts
        # Placeholder for full implementation with concept extractor
        return None

    def find_citing_cases(self, case_id: str) -> Dict[CitationRelationship, List[str]]:
        """
        Find all cases that cite a given case, grouped by relationship
        
        Args:
            case_id: Case being cited
            
        Returns:
            Dict mapping relationship type to list of citing cases
        """
        results = defaultdict(list)
        for citing_case, rel_type in self.reverse_citations[case_id]:
            results[rel_type].append(citing_case)
        return dict(results)

    def find_cited_cases(self, case_id: str) -> Dict[CitationRelationship, List[str]]:
        """
        Find all cases cited by a given case, grouped by relationship
        
        Args:
            case_id: Case doing the citing
            
        Returns:
            Dict mapping relationship type to list of cited cases
        """
        results = defaultdict(list)
        for cited_case, rel_type in self.citation_graph[case_id]:
            results[rel_type].append(cited_case)
        return dict(results)

    def get_network_stats(self) -> Dict:
        """Get statistics about the citation network"""
        unique_cases = set()
        for rel in self.relationships:
            unique_cases.add(rel.citing_case_id)
            unique_cases.add(rel.cited_case_id)
        
        overruled_count = len([r for r in self.case_status.values() if r.is_overruled])
        good_law_count = len([r for r in self.case_status.values() if r.current_status == "good law"])
        
        return {
            "total_relationships": len(self.relationships),
            "unique_cases": len(unique_cases),
            "good_law_cases": good_law_count,
            "overruled_cases": overruled_count,
            "relationship_types": self._count_relationship_types(),
        }

    def _count_relationship_types(self) -> Dict[str, int]:
        """Count citations by type"""
        counts = defaultdict(int)
        for rel in self.relationships:
            counts[rel.relationship_type.value] += 1
        return dict(counts)

    def export_network_graph(self, filepath: str):
        """
        Export citation network to JSON format
        
        Args:
            filepath: Path to save JSON
        """
        data = {
            "relationships": [asdict(r) for r in self.relationships],
            "case_statuses": {
                case_id: asdict(status)
                for case_id, status in self.case_status.items()
            },
            "stats": self.get_network_stats(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def import_network_graph(self, filepath: str):
        """
        Import citation network from JSON
        
        Args:
            filepath: Path to JSON file
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Reconstruct relationships
        self.relationships = []
        for rel_data in data.get("relationships", []):
            rel_data["relationship_type"] = CitationRelationship(rel_data["relationship_type"])
            self.relationships.append(CaseRelationship(**rel_data))
            # Rebuild graph
            case_id = rel_data["citing_case_id"]
            cited = rel_data["cited_case_id"]
            self.citation_graph[case_id].append((cited, rel_data["relationship_type"]))
            self.reverse_citations[cited].append((case_id, rel_data["relationship_type"]))


# Global citation network
_citation_network = None


def get_citation_network() -> CitationNetworkGraph:
    """Get or create global citation network"""
    global _citation_network
    if _citation_network is None:
        _citation_network = CitationNetworkGraph()
    return _citation_network
