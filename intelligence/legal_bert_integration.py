"""
Legal-BERT Integration Module

Provides semantic search capabilities using Legal-BERT or similar transformer models
fine-tuned on legal text. Enables concept-based search beyond keyword matching.

Features:
- Case embedding and semantic similarity
- Legal concept extraction
- Contextual case retrieval
- Query expansion for legal terms
"""

import json
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import os
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer, util
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


@dataclass
class SemanticSearchResult:
    """Result from semantic search query"""
    case_id: str
    case_name: str
    similarity_score: float
    excerpt: str
    legal_issues: List[str]


class LegalBertIntegration:
    """
    Semantic search engine using Legal-BERT embeddings
    
    Models available:
    - "sentence-transformers/legal-bert-base-uncased" (recommended for legal text)
    - "sentence-transformers/all-mpnet-base-v2" (general purpose, works well)
    - "sentence-transformers/all-MiniLM-L6-v2" (lightweight, faster)
    """

    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        """
        Initialize Legal-BERT model
        
        Args:
            model_name: HuggingFace model identifier
        """
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError(
                "sentence-transformers required for semantic search. "
                "Install with: pip install sentence-transformers"
            )
        
        self.model_name = model_name
        self.model = None
        self.case_embeddings = {}  # cache: case_id -> embedding
        self.embedding_cache_path = Path("data/embeddings/cache.json")
        self.embedding_dir = Path("data/embeddings")
        
        self._initialize_model()
        self._load_cached_embeddings()

    def _initialize_model(self):
        """Load the model (lazy initialization)"""
        try:
            print(f"Loading {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            print("✓ Model loaded successfully")
        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            raise

    def _load_cached_embeddings(self):
        """Load previously computed embeddings from cache"""
        if self.embedding_cache_path.exists():
            try:
                with open(self.embedding_cache_path, 'r') as f:
                    cached = json.load(f)
                    # Convert lists back to numpy arrays
                    self.case_embeddings = {
                        case_id: np.array(emb)
                        for case_id, emb in cached.items()
                    }
                print(f"✓ Loaded {len(self.case_embeddings)} cached embeddings")
            except Exception as e:
                print(f"Could not load embeddings cache: {e}")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            numpy array of embeddings
        """
        if not self.model:
            raise RuntimeError("Model not initialized")
        
        # Truncate to reasonable length (512 tokens ~= 2000 chars)
        text = text[:2000]
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def embed_case(self, case_id: str, full_text: str) -> np.ndarray:
        """
        Generate and cache embedding for a case
        
        Args:
            case_id: Unique case identifier
            full_text: Complete judgment text
            
        Returns:
            numpy array of embeddings
        """
        if case_id in self.case_embeddings:
            return self.case_embeddings[case_id]
        
        embedding = self.embed_text(full_text)
        self.case_embeddings[case_id] = embedding
        return embedding

    def semantic_search(
        self,
        query: str,
        case_embeddings_dict: Dict[str, np.ndarray],
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Semantic search across cases
        
        Args:
            query: Natural language search query
            case_embeddings_dict: Dict of case_id -> embedding vectors
            top_k: Number of results to return
            
        Returns:
            List of (case_id, similarity_score) tuples
        """
        if not case_embeddings_dict:
            return []
        
        # Embed query
        query_embedding = self.embed_text(query)
        
        # Compute similarities
        similarities = []
        for case_id, case_embedding in case_embeddings_dict.items():
            # Cosine similarity
            similarity = util.pytorch_cos_sim(query_embedding, case_embedding)[0][0].item()
            similarities.append((case_id, float(similarity)))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def find_similar_cases(
        self,
        case_id: str,
        case_embeddings_dict: Dict[str, np.ndarray],
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Find cases similar to a given case
        
        Args:
            case_id: Reference case ID
            case_embeddings_dict: Dict of all case embeddings
            top_k: Number of similar cases to return
            
        Returns:
            List of (similar_case_id, similarity_score) tuples
        """
        if case_id not in case_embeddings_dict:
            return []
        
        reference_embedding = case_embeddings_dict[case_id]
        
        similarities = []
        for other_case_id, other_embedding in case_embeddings_dict.items():
            if other_case_id == case_id:
                continue
            
            similarity = util.pytorch_cos_sim(reference_embedding, other_embedding)[0][0].item()
            similarities.append((other_case_id, float(similarity)))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def batch_embed_cases(self, cases: List[Tuple[str, str]]) -> Dict[str, np.ndarray]:
        """
        Efficiently embed multiple cases
        
        Args:
            cases: List of (case_id, full_text) tuples
            
        Returns:
            Dict of case_id -> embedding
        """
        result = {}
        for case_id, text in cases:
            if case_id not in self.case_embeddings:
                result[case_id] = self.embed_case(case_id, text)
            else:
                result[case_id] = self.case_embeddings[case_id]
        return result

    def cache_embeddings(self):
        """Save embeddings cache to disk"""
        self.embedding_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert numpy arrays to lists for JSON serialization
        cache_data = {
            case_id: emb.tolist()
            for case_id, emb in self.case_embeddings.items()
        }
        
        with open(self.embedding_cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        print(f"✓ Cached {len(cache_data)} embeddings")

    def get_embedding_stats(self) -> Dict:
        """Get statistics about cached embeddings"""
        return {
            "cached_cases": len(self.case_embeddings),
            "model_name": self.model_name,
            "embedding_dimension": len(next(iter(self.case_embeddings.values()))) if self.case_embeddings else 0,
        }


class LegalConceptMatcher:
    """
    Uses embeddings to match cases to legal concepts
    """

    def __init__(self, bert_integration: LegalBertIntegration):
        """
        Initialize concept matcher
        
        Args:
            bert_integration: LegalBertIntegration instance
        """
        self.bert = bert_integration
        self.concept_embeddings = {}
        self._initialize_concept_embeddings()

    def _initialize_concept_embeddings(self):
        """Pre-compute embeddings for key legal concepts"""
        from utils.legal_taxonomy import get_taxonomy
        
        taxonomy = get_taxonomy()
        concepts = taxonomy.get_all_concepts()
        
        print(f"Computing embeddings for {len(concepts)} legal concepts...")
        for concept in concepts:
            concept_text = f"{concept.name}: {concept.definition}"
            self.concept_embeddings[concept.id] = self.bert.embed_text(concept_text)

    def match_concepts(
        self,
        case_text: str,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Match case to top legal concepts
        
        Args:
            case_text: Case judgment text
            top_k: Number of concepts to return
            
        Returns:
            List of (concept_id, similarity_score) tuples
        """
        case_embedding = self.bert.embed_text(case_text)
        
        similarities = []
        for concept_id, concept_embedding in self.concept_embeddings.items():
            similarity = util.pytorch_cos_sim(case_embedding, concept_embedding)[0][0].item()
            similarities.append((concept_id, float(similarity)))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def concept_based_search(
        self,
        concept_id: str,
        case_embeddings_dict: Dict[str, np.ndarray],
        threshold: float = 0.5,
        top_k: int = 20
    ) -> List[Tuple[str, float]]:
        """
        Find cases related to a specific legal concept
        
        Args:
            concept_id: Concept to search for
            case_embeddings_dict: Dict of case embeddings
            threshold: Minimum similarity score
            top_k: Maximum results
            
        Returns:
            List of (case_id, similarity_score) tuples
        """
        if concept_id not in self.concept_embeddings:
            return []
        
        concept_embedding = self.concept_embeddings[concept_id]
        
        similarities = []
        for case_id, case_embedding in case_embeddings_dict.items():
            similarity = util.pytorch_cos_sim(concept_embedding, case_embedding)[0][0].item()
            if similarity >= threshold:
                similarities.append((case_id, float(similarity)))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


# Lazy initialization for optional dependency
_bert_instance = None


def get_bert_integration(model_name: str = "sentence-transformers/all-mpnet-base-v2") -> Optional[LegalBertIntegration]:
    """
    Get or create Legal-BERT integration instance
    
    Args:
        model_name: HuggingFace model identifier
        
    Returns:
        LegalBertIntegration instance or None if dependencies not installed
    """
    global _bert_instance
    
    if not HAS_SENTENCE_TRANSFORMERS:
        print("⚠ sentence-transformers not installed. Semantic search unavailable.")
        print("  Install with: pip install sentence-transformers torch")
        return None
    
    if _bert_instance is None:
        try:
            _bert_instance = LegalBertIntegration(model_name)
        except Exception as e:
            print(f"Failed to initialize Legal-BERT: {e}")
            return None
    
    return _bert_instance
