"""Intelligence layer for GLIS - semantic search and concept analysis"""

from .legal_bert_integration import LegalBertIntegration, LegalConceptMatcher, get_bert_integration
from .citation_network import CitationNetworkGraph, CitationRelationship, CitationStatus, get_citation_network
from .concept_extractor import LegalConceptExtractor, ExtractedConcept, get_concept_extractor

__all__ = [
    "LegalBertIntegration",
    "LegalConceptMatcher",
    "get_bert_integration",
    "CitationNetworkGraph",
    "CitationRelationship",
    "CitationStatus",
    "get_citation_network",
    "LegalConceptExtractor",
    "ExtractedConcept",
    "get_concept_extractor",
]
