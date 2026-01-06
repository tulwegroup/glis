"""
Legal Concept Extractor Module

Extracts and maps legal concepts from case judgments to the Ghana legal taxonomy.
Uses keyword matching, pattern recognition, and semantic similarity.

Features:
- Concept identification from judgment text
- Statute and statute provision extraction
- Ratio decidendi extraction
- Legal principle identification
- Concept relationship mapping
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from utils.legal_taxonomy import get_taxonomy, LegalConcept


@dataclass
class ExtractedConcept:
    """Extracted legal concept from judgment"""
    concept_id: str
    concept_name: str
    confidence: float  # 0-1: confidence of extraction
    occurrences: int  # How many times mentioned
    context_passages: List[str]  # Passages where it appears
    related_statutes: List[str]
    related_concepts: List[str]


@dataclass
class ExtractedPrinciple:
    """Extracted legal principle from judgment"""
    principle: str
    supporting_concept: str
    context: str
    is_ratio_decidendi: bool  # True if part of main holding


class LegalConceptExtractor:
    """
    Extracts legal concepts and principles from case text
    """

    def __init__(self):
        self.taxonomy = get_taxonomy()
        self.statute_pattern = self._compile_statute_patterns()

    def _compile_statute_patterns(self) -> re.Pattern:
        """Compile regex patterns for statute references"""
        patterns = [
            r"(?:Act|Constitution|Ordinance|Law|PNDCL|L\.I\.)\s+(?:No\.)?\s*(\d+)?[,\s]*(\d{4})?",
            r"(?:Section|Article|S|Art)\.\s*(\d+(?:\(\w+\))?)",
            r"(\w+\s+Act(?:\s+\([^)]*\))?)",
            r"Ghana(?:ian)?\s+(?:Constitution|Criminal\s+Code|Companies\s+Act)",
        ]
        combined = "|".join(f"({p})" for p in patterns)
        return re.compile(combined, re.IGNORECASE)

    def extract_concepts(self, case_text: str, top_k: int = 10) -> List[ExtractedConcept]:
        """
        Extract top legal concepts from case text
        
        Args:
            case_text: Full judgment text
            top_k: Number of concepts to return
            
        Returns:
            List of extracted concepts ranked by confidence
        """
        text_lower = case_text.lower()
        extracted = {}
        
        # Get all concepts from taxonomy
        all_concepts = self.taxonomy.get_all_concepts()
        
        for concept in all_concepts:
            # Check for concept name and aliases
            search_terms = [concept.name.lower()] + [a.lower() for a in concept.aliases]
            
            occurrences = 0
            context_passages = []
            confidence = 0.0
            
            for term in search_terms:
                # Count occurrences
                term_pattern = r'\b' + re.escape(term) + r'\b'
                matches = list(re.finditer(term_pattern, text_lower))
                occurrences += len(matches)
                
                # Extract context around matches
                for match in matches:
                    start = max(0, match.start() - 150)
                    end = min(len(case_text), match.end() + 150)
                    passage = case_text[start:end].strip()
                    context_passages.append(passage)
            
            # Calculate confidence based on occurrences and keyword specificity
            if occurrences > 0:
                # More specific terms get higher confidence
                term_length = len(max(search_terms, key=len))
                confidence = min(1.0, (occurrences / 10.0) * (term_length / 50.0))
                
                # Extract related statutes mentioned in context
                related_statutes = self._extract_statutes_from_passages(context_passages)
                
                extracted[concept.id] = ExtractedConcept(
                    concept_id=concept.id,
                    concept_name=concept.name,
                    confidence=confidence,
                    occurrences=occurrences,
                    context_passages=context_passages[:3],  # Limit to 3 passages
                    related_statutes=related_statutes,
                    related_concepts=[]
                )
        
        # Sort by confidence and return top_k
        sorted_concepts = sorted(
            extracted.values(),
            key=lambda x: (x.confidence, x.occurrences),
            reverse=True
        )
        return sorted_concepts[:top_k]

    def extract_statutes(self, case_text: str) -> List[Tuple[str, List[int]]]:
        """
        Extract statute references from case text
        
        Args:
            case_text: Full judgment text
            
        Returns:
            List of (statute_name, section_numbers) tuples
        """
        statutes = {}
        
        # Find statute references
        statute_matches = re.finditer(self.statute_pattern, case_text)
        for match in statute_matches:
            matched_text = match.group()
            
            # Try to identify statute
            statute_name = self._identify_statute(matched_text)
            if statute_name:
                if statute_name not in statutes:
                    statutes[statute_name] = []
                
                # Extract section numbers if present
                section_matches = re.findall(r"[Ss]ection\s+(\d+(?:\([^)]*\))?)", matched_text)
                statutes[statute_name].extend([int(s.split('(')[0]) for s in section_matches])
        
        return list(statutes.items())

    def _identify_statute(self, text: str) -> Optional[str]:
        """Identify specific statute from text"""
        statute_map = {
            "Act 992": "Companies Act (Act 992, 2019)",
            "Act 29": "Criminal Code (Act 29, 1960)",
            "Act 25": "Contracts Act (Act 25, 1960)",
            "Act 137": "Sale of Goods Act (Act 137, 1962)",
            "Act 367": "Matrimonial Causes Act (Act 367, 1971)",
            "PNDCL 111": "Intestate Succession Law (PNDCL 111, 1985)",
            "PNDCL 152": "Land Title Registration Law (PNDCL 152, 1986)",
        }
        
        text_upper = text.upper()
        for key, full_name in statute_map.items():
            if key in text_upper:
                return full_name
        
        return None

    def _extract_statutes_from_passages(self, passages: List[str]) -> List[str]:
        """Extract statute names from text passages"""
        statutes = set()
        for passage in passages:
            extracted = self.extract_statutes(passage)
            for statute_name, _ in extracted:
                statutes.add(statute_name)
        return list(statutes)

    def extract_ratio_decidendi(self, case_text: str) -> List[ExtractedPrinciple]:
        """
        Extract ratio decidendi (main holding) from judgment
        
        Args:
            case_text: Full judgment text
            
        Returns:
            List of extracted legal principles
        """
        principles = []
        
        # Look for judgment conclusion section
        # These typically start with phrases like "In the result", "We hold", "The court found"
        conclusion_markers = [
            r"(?:In\s+the\s+result|In\s+conclusion|We\s+hold|We\s+find|The\s+court\s+(?:found|holds)|Accordingly)",
        ]
        
        for marker in conclusion_markers:
            matches = re.finditer(marker, case_text, re.IGNORECASE)
            for match in matches:
                # Extract text after marker (usually follows next 500 chars)
                start = match.start()
                end = min(len(case_text), start + 500)
                principle_text = case_text[start:end]
                
                # Extract related concepts
                extracted_concepts = self.extract_concepts(principle_text, top_k=3)
                
                for concept in extracted_concepts:
                    principle = ExtractedPrinciple(
                        principle=principle_text.strip(),
                        supporting_concept=concept.concept_name,
                        context=principle_text,
                        is_ratio_decidendi=True
                    )
                    principles.append(principle)
        
        return principles

    def map_concepts_to_taxonomy(
        self,
        case_text: str
    ) -> Dict[str, ExtractedConcept]:
        """
        Map all concepts in a case to taxonomy
        
        Args:
            case_text: Full judgment text
            
        Returns:
            Dict of concept_id -> ExtractedConcept
        """
        concepts = self.extract_concepts(case_text, top_k=100)
        return {c.concept_id: c for c in concepts}

    def analyze_legal_focus(self, case_text: str) -> Dict[str, float]:
        """
        Determine main legal areas covered in case
        
        Args:
            case_text: Full judgment text
            
        Returns:
            Dict of legal_category -> focus_score (0-1)
        """
        categories = self.taxonomy.get_categories()
        scores = {}
        
        for category in categories:
            concepts = self.taxonomy.get_concepts_by_category(category)
            category_score = 0.0
            
            for concept in concepts:
                text_lower = case_text.lower()
                concept_lower = concept.name.lower()
                occurrences = len(re.findall(r'\b' + re.escape(concept_lower) + r'\b', text_lower))
                category_score += occurrences * 0.1
            
            scores[category] = min(1.0, category_score)
        
        # Normalize scores
        max_score = max(scores.values()) if scores.values() else 1.0
        if max_score > 0:
            scores = {k: v / max_score for k, v in scores.items()}
        
        return scores

    def get_extraction_summary(self, case_text: str) -> Dict:
        """
        Get summary of all extracted information from case
        
        Args:
            case_text: Full judgment text
            
        Returns:
            Summary dict with concepts, statutes, principles
        """
        concepts = self.extract_concepts(case_text, top_k=10)
        statutes = self.extract_statutes(case_text)
        principles = self.extract_ratio_decidendi(case_text)
        legal_focus = self.analyze_legal_focus(case_text)
        
        return {
            "top_concepts": [
                {
                    "concept": c.concept_name,
                    "confidence": c.confidence,
                    "occurrences": c.occurrences,
                }
                for c in concepts
            ],
            "statutes_cited": statutes,
            "key_principles": [
                {
                    "principle": p.principle,
                    "concept": p.supporting_concept,
                }
                for p in principles
            ],
            "legal_focus": {k: round(v, 2) for k, v in legal_focus.items() if v > 0.2},
        }


# Global extractor instance
_extractor = None


def get_concept_extractor() -> LegalConceptExtractor:
    """Get or create global concept extractor"""
    global _extractor
    if _extractor is None:
        _extractor = LegalConceptExtractor()
    return _extractor
