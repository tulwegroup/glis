"""
Case Brief Generator - Layer 3

Generates structured case briefs using LLM and legal analysis tools.
Creates Facts, Issue, Holding, and Reasoning sections automatically.

Features:
- Structured brief generation (FIHR format)
- Multi-section analysis
- Case comparison and distinction
- Custom brief templates
- Export to Word, PDF, and JSON
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json

from reasoning.llm_integration import (
    get_llm_orchestrator, 
    TaskType, 
    LLMResponse
)
from reasoning.precedent_analyzer import (
    get_precedent_analyzer,
    PrecedentCaseInfo
)
from intelligence.concept_extractor import get_concept_extractor
from intelligence.citation_network import get_citation_network


@dataclass
class BriefSection:
    """Individual section of a case brief"""
    title: str
    content: str
    source: str = "llm"  # "llm", "extracted", "precedent_analysis"
    confidence: float = 1.0
    tokens_used: int = 0


@dataclass
class CaseBrief:
    """Complete structured case brief"""
    case_id: str
    case_name: str
    court: str
    year: int
    date_decided: str
    judge: str
    
    # FIHR sections
    facts: BriefSection
    issue: BriefSection
    holding: BriefSection
    reasoning: BriefSection
    
    # Additional sections
    key_concepts: List[str] = field(default_factory=list)
    cited_cases: List[Dict[str, Any]] = field(default_factory=list)
    distinguishing_factors: List[str] = field(default_factory=list)
    concurring_opinions: List[Dict[str, str]] = field(default_factory=list)
    dissenting_opinions: List[Dict[str, str]] = field(default_factory=list)
    
    # Metadata
    generation_date: str = field(default_factory=lambda: datetime.now().isoformat())
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    generation_method: str = "hybrid"  # "llm_only", "extracted_only", "hybrid"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['facts'] = asdict(self.facts)
        data['issue'] = asdict(self.issue)
        data['holding'] = asdict(self.holding)
        data['reasoning'] = asdict(self.reasoning)
        return data

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    def to_markdown(self) -> str:
        """Convert to markdown format"""
        md = f"""# Case Brief: {self.case_name}

**Citation:** {self.case_id}
**Court:** {self.court}
**Year:** {self.year}
**Date:** {self.date_decided}
**Judge:** {self.judge}

## Facts
{self.facts.content}

## Issue
{self.issue.content}

## Holding
{self.holding.content}

## Reasoning
{self.reasoning.content}

## Key Concepts
{', '.join(self.key_concepts) if self.key_concepts else 'N/A'}

## Cited Cases
"""
        if self.cited_cases:
            for case in self.cited_cases:
                md += f"- **{case.get('name', 'Unknown')}** ({case.get('citation', 'N/A')}): {case.get('relationship', 'cited')}\n"
        else:
            md += "- No cited cases\n"
        
        if self.distinguishing_factors:
            md += "\n## Distinguishing Factors\n"
            for factor in self.distinguishing_factors:
                md += f"- {factor}\n"
        
        if self.concurring_opinions:
            md += "\n## Concurring Opinions\n"
            for opinion in self.concurring_opinions:
                md += f"- **{opinion.get('justice', 'Unknown')}**: {opinion.get('text', '')}\n"
        
        if self.dissenting_opinions:
            md += "\n## Dissenting Opinions\n"
            for opinion in self.dissenting_opinions:
                md += f"- **{opinion.get('justice', 'Unknown')}**: {opinion.get('text', '')}\n"
        
        md += f"\n---\n*Brief generated on {self.generation_date}*"
        return md


@dataclass
class BriefComparison:
    """Comparison between multiple cases"""
    cases: List[CaseBrief]
    comparison_date: str = field(default_factory=lambda: datetime.now().isoformat())
    similarities: List[Dict[str, Any]] = field(default_factory=list)
    differences: List[Dict[str, Any]] = field(default_factory=list)
    key_distinctions: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert comparison to markdown"""
        md = "# Case Comparison\n\n"
        
        # Header with all cases
        case_names = " vs. ".join([case.case_name for case in self.cases])
        md += f"## {case_names}\n\n"
        
        # Comparison table
        md += "| Factor | " + " | ".join([case.case_name[:20] for case in self.cases]) + " |\n"
        md += "|--------|" + "|".join(["-----" for _ in self.cases]) + "|\n"
        
        # Add key facts
        md += "| Facts | " + " | ".join([case.facts.content[:50] + "..." for case in self.cases]) + " |\n"
        md += "| Issue | " + " | ".join([case.issue.content[:50] + "..." for case in self.cases]) + " |\n"
        md += "| Holding | " + " | ".join([case.holding.content[:50] + "..." for case in self.cases]) + " |\n"
        
        if self.similarities:
            md += "\n## Similarities\n"
            for sim in self.similarities:
                md += f"- {sim.get('description', 'N/A')}\n"
        
        if self.differences:
            md += "\n## Differences\n"
            for diff in self.differences:
                md += f"- {diff.get('description', 'N/A')}\n"
        
        if self.key_distinctions:
            md += "\n## Key Distinctions\n"
            for dist in self.key_distinctions:
                md += f"- {dist}\n"
        
        return md


class CaseBriefGenerator:
    """Generate case briefs using LLM and extracted analysis"""

    def __init__(self):
        self.llm = get_llm_orchestrator()
        self.precedent_analyzer = get_precedent_analyzer()
        self.concept_extractor = get_concept_extractor()
        self.citation_network = get_citation_network()

    def generate_brief(
        self,
        case_id: str,
        case_name: str,
        case_text: str,
        metadata: Dict[str, Any],
        use_llm: bool = True,
        use_extraction: bool = True,
    ) -> CaseBrief:
        """Generate complete case brief"""
        
        # Extract basic metadata
        court = metadata.get('court', 'Ghana Supreme Court')
        year = metadata.get('year', datetime.now().year)
        date_decided = metadata.get('date_decided', '')
        judge = metadata.get('judge', '')
        
        total_tokens = 0
        total_cost = 0.0
        
        # Generate Facts section
        facts_response = self.llm.generate_from_template(
            "brief_facts",
            case_text=case_text
        )
        facts_section = BriefSection(
            title="Facts",
            content=facts_response.text,
            source="llm",
            tokens_used=facts_response.tokens_used
        )
        total_tokens += facts_response.tokens_used
        total_cost += facts_response.cost_usd
        
        # Generate Issue section
        issue_response = self.llm.generate_from_template(
            "brief_issue",
            case_text=case_text
        )
        issue_section = BriefSection(
            title="Issue",
            content=issue_response.text,
            source="llm",
            tokens_used=issue_response.tokens_used
        )
        total_tokens += issue_response.tokens_used
        total_cost += issue_response.cost_usd
        
        # Generate Holding section
        holding_response = self.llm.generate_from_template(
            "brief_holding",
            case_text=case_text
        )
        holding_section = BriefSection(
            title="Holding",
            content=holding_response.text,
            source="llm",
            tokens_used=holding_response.tokens_used
        )
        total_tokens += holding_response.tokens_used
        total_cost += holding_response.cost_usd
        
        # Generate Reasoning section (longer analysis)
        reasoning_prompt = f"""Provide the court's legal reasoning and analysis for this case:

Case: {case_name}

Full Text:
{case_text[:2000]}

Legal Reasoning:"""
        
        reasoning_response = self.llm.generate(
            reasoning_prompt,
            task_type=TaskType.BRIEF_GENERATION
        )
        reasoning_section = BriefSection(
            title="Reasoning",
            content=reasoning_response.text,
            source="llm",
            tokens_used=reasoning_response.tokens_used
        )
        total_tokens += reasoning_response.tokens_used
        total_cost += reasoning_response.cost_usd
        
        # Extract concepts
        concepts = self.concept_extractor.extract_concepts(case_text)
        key_concepts = [c.name for c in concepts.concepts[:5]]
        
        # Extract citations
        citations = self.citation_network.extract_citations(case_text)
        cited_cases = [
            {
                "citation": c.citation,
                "name": c.case_name,
                "relationship": c.relationship.value if c.relationship else "cited"
            }
            for c in citations
        ]
        
        # Build brief
        brief = CaseBrief(
            case_id=case_id,
            case_name=case_name,
            court=court,
            year=year,
            date_decided=date_decided,
            judge=judge,
            facts=facts_section,
            issue=issue_section,
            holding=holding_section,
            reasoning=reasoning_section,
            key_concepts=key_concepts,
            cited_cases=cited_cases,
            total_tokens_used=total_tokens,
            total_cost_usd=total_cost,
            generation_method="hybrid" if (use_llm and use_extraction) else ("llm_only" if use_llm else "extracted_only")
        )
        
        return brief

    def generate_brief_from_precedent(
        self,
        precedent: PrecedentCaseInfo
    ) -> CaseBrief:
        """Generate brief from precedent case info"""
        return self.generate_brief(
            case_id=precedent.case_id,
            case_name=precedent.case_name,
            case_text=precedent.key_passage or "",
            metadata={
                'court': precedent.court,
                'year': int(precedent.case_id.split('/')[-1].split()[0]) if '/' in precedent.case_id else datetime.now().year,
                'date_decided': precedent.date_decided,
                'judge': ''
            }
        )

    def compare_cases(
        self,
        briefs: List[CaseBrief],
        focus_areas: Optional[List[str]] = None
    ) -> BriefComparison:
        """Compare multiple case briefs"""
        
        comparison = BriefComparison(cases=briefs)
        
        # Extract similarities
        all_concepts = set()
        for brief in briefs:
            all_concepts.update(brief.key_concepts)
        
        if all_concepts:
            comparison.similarities.append({
                "description": f"All cases involve these concepts: {', '.join(list(all_concepts)[:3])}",
                "type": "concepts"
            })
        
        # Extract holdings
        holdings = [brief.holding.content for brief in briefs]
        if len(set(holdings)) == 1:
            comparison.similarities.append({
                "description": "All cases reach the same holding",
                "type": "holding"
            })
        else:
            for i, brief1 in enumerate(briefs):
                for brief2 in briefs[i+1:]:
                    if brief1.holding.content != brief2.holding.content:
                        comparison.differences.append({
                            "description": f"{brief1.case_name} vs {brief2.case_name}: Different holdings",
                            "type": "holding"
                        })
        
        # Compare key facts
        fact_sets = [set(brief.facts.content.split()[:10]) for brief in briefs]
        overlap = len(fact_sets[0].intersection(*fact_sets[1:]))
        if overlap > 5:
            comparison.similarities.append({
                "description": "Cases share similar factual patterns",
                "type": "facts"
            })
        
        return comparison

    def generate_batch_briefs(
        self,
        cases: List[Dict[str, Any]]
    ) -> List[CaseBrief]:
        """Generate briefs for multiple cases"""
        briefs = []
        for case_data in cases:
            try:
                brief = self.generate_brief(
                    case_id=case_data.get('case_id', ''),
                    case_name=case_data.get('case_name', ''),
                    case_text=case_data.get('case_text', ''),
                    metadata=case_data.get('metadata', {})
                )
                briefs.append(brief)
            except Exception as e:
                print(f"Error generating brief for {case_data.get('case_name', 'Unknown')}: {e}")
                continue
        
        return briefs


# Global instance
_generator: Optional[CaseBriefGenerator] = None


def get_case_brief_generator() -> CaseBriefGenerator:
    """Get or create case brief generator singleton"""
    global _generator
    if _generator is None:
        _generator = CaseBriefGenerator()
    return _generator


if __name__ == "__main__":
    # Test brief generation
    generator = get_case_brief_generator()
    
    test_case = {
        'case_id': 'GHASC/2023/001',
        'case_name': 'Test v. Defendant',
        'case_text': 'Sample case text for testing brief generation...',
        'metadata': {
            'court': 'Ghana Supreme Court',
            'year': 2023,
            'date_decided': '2023-01-15',
            'judge': 'Anin-Yeboah JSC'
        }
    }
    
    print("Generating brief...")
    # brief = generator.generate_brief(**test_case)
    # print(brief.to_markdown())
