"""
Strategy Simulator - Layer 3

Predicts litigation outcomes and provides strategic recommendations.
Analyzes precedent strength, risk factors, and cost estimation.

Features:
- Outcome prediction based on precedents
- Risk assessment and probability scoring
- Cost estimation and financial analysis
- Strategy comparison and recommendations
- Scenario simulation
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import math

from reasoning.llm_integration import (
    get_llm_orchestrator,
    TaskType
)
from reasoning.precedent_analyzer import get_precedent_analyzer
from intelligence.citation_network import get_citation_network, CitationRelationship


class OutcomeType(Enum):
    """Possible litigation outcomes"""
    PLAINTIFF_WIN = "plaintiff_win"
    DEFENDANT_WIN = "defendant_win"
    SETTLEMENT = "settlement"
    JUDGMENT_ON_MERITS = "judgment_on_merits"
    SUMMARY_JUDGMENT = "summary_judgment"
    DISMISSAL = "dismissal"
    APPEAL = "appeal"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Risk assessment levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


@dataclass
class RiskFactor:
    """Individual risk factor assessment"""
    name: str
    category: str  # "factual", "legal", "procedural", "financial", "reputational"
    impact: float  # 0-1, higher = more negative
    likelihood: float  # 0-1, probability of occurring
    mitigation: Optional[str] = None
    estimated_cost: float = 0.0

    def calculate_risk_score(self) -> float:
        """Calculate risk score as impact × likelihood"""
        return self.impact * self.likelihood


@dataclass
class PrecedentStrength:
    """Analysis of precedent support for position"""
    case_name: str
    case_citation: str
    year: int
    authority_level: str  # "binding", "persuasive", "weak"
    similarity_score: float  # 0-1
    supporting_holding: bool
    distinguishable: bool
    distinguishing_factors: List[str] = field(default_factory=list)

    def calculate_strength_score(self) -> float:
        """Calculate overall strength"""
        base = self.similarity_score
        
        # Authority multiplier
        authority_mult = {
            "binding": 1.0,
            "persuasive": 0.7,
            "weak": 0.3
        }.get(self.authority_level, 0.5)
        
        # Supporting holding bonus
        holding_mult = 1.2 if self.supporting_holding else 0.8
        
        # Distinguishability penalty
        distinguish_mult = 0.6 if self.distinguishable else 1.0
        
        return base * authority_mult * holding_mult * distinguish_mult


@dataclass
class CostEstimate:
    """Estimated litigation costs"""
    attorney_fees: float  # Base hourly rate estimate
    court_filing_fees: float
    expert_witnesses: float
    discovery_costs: float  # Document review, subpoenas
    deposition_costs: float
    trial_preparation: float
    appeal_costs: float  # If applicable
    miscellaneous: float = 0.0
    duration_days: int = 365  # Estimated duration
    hourly_rate: float = 500.0  # Avg Ghana lawyer hourly rate

    @property
    def total_cost(self) -> float:
        """Calculate total estimated cost"""
        return (
            self.attorney_fees +
            self.court_filing_fees +
            self.expert_witnesses +
            self.discovery_costs +
            self.deposition_costs +
            self.trial_preparation +
            self.appeal_costs +
            self.miscellaneous
        )

    @property
    def attorney_hours_estimate(self) -> float:
        """Estimate total attorney hours"""
        return self.attorney_fees / self.hourly_rate if self.hourly_rate > 0 else 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'attorney_fees': self.attorney_fees,
            'court_filing_fees': self.court_filing_fees,
            'expert_witnesses': self.expert_witnesses,
            'discovery_costs': self.discovery_costs,
            'deposition_costs': self.deposition_costs,
            'trial_preparation': self.trial_preparation,
            'appeal_costs': self.appeal_costs,
            'miscellaneous': self.miscellaneous,
            'total_cost': self.total_cost,
            'duration_days': self.duration_days,
            'attorney_hours_estimate': self.attorney_hours_estimate
        }


@dataclass
class OutcomePrediction:
    """Predicted litigation outcome"""
    primary_outcome: OutcomeType
    outcome_probability: float  # 0-1
    confidence: float  # 0-1, confidence in prediction
    reasoning: str
    supporting_factors: List[str] = field(default_factory=list)
    opposing_factors: List[str] = field(default_factory=list)
    timeline_estimate: int = 365  # Days to resolution
    likely_damages: Optional[float] = None  # If plaintiff win
    settlement_range: Tuple[float, float] = (0.0, 0.0)  # Min-max settlement


@dataclass
class StrategyAssessment:
    """Assessment of litigation strategy"""
    strategy_name: str
    strategy_description: str
    
    # Assessments
    legal_strength: float  # 0-1
    factual_strength: float  # 0-1
    procedural_readiness: float  # 0-1
    
    # Predictions
    predicted_outcome: OutcomePrediction
    risk_assessment: Dict[str, Any]
    cost_estimate: CostEstimate
    supporting_precedents: List[PrecedentStrength] = field(default_factory=list)
    challenging_precedents: List[PrecedentStrength] = field(default_factory=list)
    
    # Recommendations
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    assessment_date: str = field(default_factory=lambda: datetime.now().isoformat())
    overall_score: float = 0.0

    def calculate_overall_score(self) -> float:
        """Calculate overall strategy strength (0-100)"""
        # Weight various factors
        weighted_score = (
            self.legal_strength * 30 +
            self.factual_strength * 25 +
            self.procedural_readiness * 15 +
            (self.predicted_outcome.outcome_probability * 20) +
            (self.predicted_outcome.confidence * 10)
        ) / 100
        
        self.overall_score = weighted_score * 100
        return self.overall_score

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'strategy_name': self.strategy_name,
            'strategy_description': self.strategy_description,
            'legal_strength': self.legal_strength,
            'factual_strength': self.factual_strength,
            'procedural_readiness': self.procedural_readiness,
            'overall_score': self.overall_score,
            'predicted_outcome': {
                'type': self.predicted_outcome.primary_outcome.value,
                'probability': self.predicted_outcome.outcome_probability,
                'confidence': self.predicted_outcome.confidence
            },
            'cost_estimate': self.cost_estimate.to_dict(),
            'recommendations': self.recommendations
        }


@dataclass
class LitigationScenario:
    """Scenario for analysis"""
    name: str
    client_position: str  # "plaintiff" or "defendant"
    key_facts: List[str]
    legal_theories: List[str]
    opponent_strengths: List[str] = field(default_factory=list)
    opponent_weaknesses: List[str] = field(default_factory=list)


class StrategySimulator:
    """Simulate and analyze litigation strategies"""

    def __init__(self):
        self.llm = get_llm_orchestrator()
        self.precedent_analyzer = get_precedent_analyzer()
        self.citation_network = get_citation_network()

    def assess_strategy(
        self,
        scenario: LitigationScenario,
        budget: float = 50000.0
    ) -> StrategyAssessment:
        """Assess overall litigation strategy"""
        
        # Build strategy name and description
        strategy_name = f"{scenario.client_position.title()} Strategy"
        strategy_desc = f"Position: {', '.join(scenario.legal_theories[:2])}"
        
        # Calculate legal strength based on theories
        legal_strength = self._assess_legal_strength(scenario.legal_theories)
        
        # Calculate factual strength
        factual_strength = self._assess_factual_strength(
            scenario.key_facts,
            scenario.opponent_strengths,
            scenario.opponent_weaknesses
        )
        
        # Procedural readiness (assume initial 0.7)
        procedural_readiness = 0.7
        
        # Predict outcome
        predicted_outcome = self.predict_outcome(
            scenario,
            legal_strength,
            factual_strength
        )
        
        # Risk assessment
        risk_assessment = self.assess_risks(scenario)
        
        # Cost estimation
        cost_estimate = self.estimate_costs(
            complexity=max(legal_strength, factual_strength),
            budget=budget
        )
        
        # Find supporting precedents
        supporting_precedents = self._find_supporting_precedents(scenario)
        challenging_precedents = self._find_challenging_precedents(scenario)
        
        # Generate recommendations
        strengths, weaknesses, recommendations = self._generate_recommendations(
            scenario,
            legal_strength,
            factual_strength,
            predicted_outcome
        )
        
        # Build assessment
        assessment = StrategyAssessment(
            strategy_name=strategy_name,
            strategy_description=strategy_desc,
            legal_strength=legal_strength,
            factual_strength=factual_strength,
            procedural_readiness=procedural_readiness,
            predicted_outcome=predicted_outcome,
            risk_assessment=risk_assessment,
            cost_estimate=cost_estimate,
            supporting_precedents=supporting_precedents,
            challenging_precedents=challenging_precedents,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
        
        assessment.calculate_overall_score()
        return assessment

    def _assess_legal_strength(self, legal_theories: List[str]) -> float:
        """Assess strength of legal theories"""
        if not legal_theories:
            return 0.3
        
        # Heuristic scoring
        score = 0.5
        
        # More theories = slightly stronger (more bases)
        score += min(0.2, len(legal_theories) * 0.05)
        
        # Specific, established theories = stronger
        strong_theories = [
            "breach of contract", "fiduciary duty", "fraud", "negligence",
            "conversion", "trespass", "statutory violation"
        ]
        
        for theory in legal_theories:
            if any(st in theory.lower() for st in strong_theories):
                score += 0.15
        
        return min(1.0, score)

    def _assess_factual_strength(
        self,
        facts: List[str],
        opponent_strengths: List[str],
        opponent_weaknesses: List[str]
    ) -> float:
        """Assess strength of facts"""
        score = 0.5
        
        # More facts = better prepared
        score += min(0.2, len(facts) * 0.02)
        
        # Opponent weaknesses help
        score += min(0.2, len(opponent_weaknesses) * 0.05)
        
        # Opponent strengths hurt
        score -= min(0.3, len(opponent_strengths) * 0.05)
        
        return max(0.1, min(1.0, score))

    def predict_outcome(
        self,
        scenario: LitigationScenario,
        legal_strength: float,
        factual_strength: float
    ) -> OutcomePrediction:
        """Predict litigation outcome"""
        
        combined_strength = (legal_strength * 0.6) + (factual_strength * 0.4)
        
        # Determine outcome type
        if scenario.client_position == "plaintiff":
            if combined_strength > 0.7:
                outcome = OutcomeType.JUDGMENT_ON_MERITS
                probability = combined_strength
            elif combined_strength > 0.5:
                outcome = OutcomeType.SETTLEMENT
                probability = 0.7
            else:
                outcome = OutcomeType.DISMISSAL
                probability = 1.0 - combined_strength
        else:  # defendant
            if combined_strength > 0.7:
                outcome = OutcomeType.DISMISSAL
                probability = combined_strength
            elif combined_strength > 0.5:
                outcome = OutcomeType.SETTLEMENT
                probability = 0.6
            else:
                outcome = OutcomeType.JUDGMENT_ON_MERITS
                probability = 1.0 - combined_strength
        
        # Estimate settlement range (if applicable)
        settlement_range = (0.0, 0.0)
        likely_damages = None
        
        if outcome in [OutcomeType.SETTLEMENT, OutcomeType.JUDGMENT_ON_MERITS]:
            if scenario.client_position == "plaintiff":
                likely_damages = 50000 * combined_strength
                settlement_range = (25000, 75000)
        
        reasoning = self._generate_outcome_reasoning(
            scenario, combined_strength, outcome
        )
        
        return OutcomePrediction(
            primary_outcome=outcome,
            outcome_probability=min(1.0, probability),
            confidence=0.7,  # Moderate confidence in prediction
            reasoning=reasoning,
            timeline_estimate=365 + int(100 * (1 - combined_strength)),
            likely_damages=likely_damages,
            settlement_range=settlement_range
        )

    def _generate_outcome_reasoning(
        self,
        scenario: LitigationScenario,
        strength: float,
        outcome: OutcomeType
    ) -> str:
        """Generate reasoning for predicted outcome"""
        reasons = [
            f"Based on {scenario.client_position} position with {len(scenario.legal_theories)} legal theories.",
            f"Factual foundation: {len(scenario.key_facts)} supporting facts identified."
        ]
        
        if strength > 0.7:
            reasons.append("Strong legal and factual position predicts favorable outcome.")
        elif strength > 0.5:
            reasons.append("Moderate position suggests settlement as likely resolution.")
        else:
            reasons.append("Weak position indicates high risk of unfavorable judgment.")
        
        return " ".join(reasons)

    def assess_risks(self, scenario: LitigationScenario) -> Dict[str, Any]:
        """Assess litigation risks"""
        risk_factors = []
        
        # Factual risks
        if len(scenario.opponent_strengths) > 2:
            risk_factors.append(RiskFactor(
                name="Strong opponent position",
                category="factual",
                impact=0.8,
                likelihood=0.7,
                estimated_cost=5000
            ))
        
        # Legal risks
        risk_factors.append(RiskFactor(
            name="Precedent uncertainty",
            category="legal",
            impact=0.6,
            likelihood=0.5,
            estimated_cost=3000
        ))
        
        # Procedural risks
        risk_factors.append(RiskFactor(
            name="Potential procedural dismissal",
            category="procedural",
            impact=0.9,
            likelihood=0.2,
            estimated_cost=2000
        ))
        
        total_risk_score = sum(rf.calculate_risk_score() for rf in risk_factors) / len(risk_factors)
        risk_level = self._classify_risk_level(total_risk_score)
        
        return {
            'risk_level': risk_level.value,
            'risk_score': round(total_risk_score, 2),
            'risk_factors': [asdict(rf) for rf in risk_factors],
            'total_potential_loss': sum(rf.estimated_cost for rf in risk_factors)
        }

    def _classify_risk_level(self, score: float) -> RiskLevel:
        """Classify risk level from score"""
        if score < 0.1:
            return RiskLevel.VERY_LOW
        elif score < 0.25:
            return RiskLevel.LOW
        elif score < 0.5:
            return RiskLevel.MODERATE
        elif score < 0.75:
            return RiskLevel.HIGH
        elif score < 0.9:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.CRITICAL

    def estimate_costs(
        self,
        complexity: float = 0.5,
        budget: float = 50000.0
    ) -> CostEstimate:
        """Estimate litigation costs"""
        
        # Base costs scale with complexity
        complexity_multiplier = 0.5 + complexity  # 0.5 - 1.5x
        
        attorney_fees = 15000 * complexity_multiplier
        court_fees = 2000
        expert_witnesses = 10000 * complexity if complexity > 0.5 else 0
        discovery_costs = 5000 * complexity_multiplier
        deposition_costs = 3000 * complexity_multiplier if complexity > 0.6 else 0
        trial_prep = 8000 * complexity_multiplier
        appeal_costs = 5000 if complexity > 0.7 else 0
        
        return CostEstimate(
            attorney_fees=attorney_fees,
            court_filing_fees=court_fees,
            expert_witnesses=expert_witnesses,
            discovery_costs=discovery_costs,
            deposition_costs=deposition_costs,
            trial_preparation=trial_prep,
            appeal_costs=appeal_costs,
            duration_days=int(365 * complexity_multiplier)
        )

    def _find_supporting_precedents(
        self,
        scenario: LitigationScenario,
        limit: int = 3
    ) -> List[PrecedentStrength]:
        """Find precedents supporting position"""
        precedents = []
        
        for theory in scenario.legal_theories[:2]:
            try:
                # This would query actual precedent database
                precedent = PrecedentStrength(
                    case_name=f"Supporting Case ({theory})",
                    case_citation="[2023] GHASC 001",
                    year=2023,
                    authority_level="persuasive",
                    similarity_score=0.8,
                    supporting_holding=True,
                    distinguishable=False
                )
                precedents.append(precedent)
            except:
                pass
        
        return precedents[:limit]

    def _find_challenging_precedents(
        self,
        scenario: LitigationScenario,
        limit: int = 2
    ) -> List[PrecedentStrength]:
        """Find precedents challenging position"""
        precedents = []
        
        for strength in scenario.opponent_strengths[:1]:
            try:
                precedent = PrecedentStrength(
                    case_name=f"Challenging Case ({strength})",
                    case_citation="[2022] GHASC 045",
                    year=2022,
                    authority_level="persuasive",
                    similarity_score=0.6,
                    supporting_holding=False,
                    distinguishable=True,
                    distinguishing_factors=["Different jurisdiction", "Different statute"]
                )
                precedents.append(precedent)
            except:
                pass
        
        return precedents[:limit]

    def _generate_recommendations(
        self,
        scenario: LitigationScenario,
        legal_strength: float,
        factual_strength: float,
        outcome: OutcomePrediction
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate strategic recommendations"""
        
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Assess legal theories
        if legal_strength > 0.7:
            strengths.append("Strong legal foundation with multiple supporting theories")
            recommendations.append("Lead with strongest legal theory in pleadings")
        else:
            weaknesses.append("Limited legal precedent support")
            recommendations.append("Conduct targeted legal research for emerging precedents")
        
        # Assess facts
        if factual_strength > 0.7:
            strengths.append("Strong factual support for position")
            recommendations.append("Prepare comprehensive factual narrative")
        else:
            weaknesses.append("Gaps in factual support")
            recommendations.append("Consider early settlement negotiations")
        
        # Outcome assessment
        if outcome.outcome_probability > 0.6:
            recommendations.append(f"Pursue aggressive litigation strategy toward {outcome.primary_outcome.value}")
        elif outcome.outcome_probability < 0.4:
            recommendations.append("Consider settlement or alternative dispute resolution")
        else:
            recommendations.append("Evaluate both litigation and settlement options")
        
        recommendations.append("Engage expert witnesses for complex technical issues")
        recommendations.append("Document all communications and maintain detailed file")
        
        return strengths, weaknesses, recommendations

    def compare_strategies(
        self,
        scenarios: List[LitigationScenario],
        budget: float = 50000.0
    ) -> List[StrategyAssessment]:
        """Compare multiple litigation strategies"""
        assessments = []
        
        for scenario in scenarios:
            assessment = self.assess_strategy(scenario, budget)
            assessments.append(assessment)
        
        # Sort by overall score (highest first)
        return sorted(assessments, key=lambda a: a.overall_score, reverse=True)


# Global instance
_simulator: Optional[StrategySimulator] = None


def get_strategy_simulator() -> StrategySimulator:
    """Get or create strategy simulator singleton"""
    global _simulator
    if _simulator is None:
        _simulator = StrategySimulator()
    return _simulator


if __name__ == "__main__":
    # Test strategy simulator
    simulator = get_strategy_simulator()
    
    test_scenario = LitigationScenario(
        name="Contract Breach Case",
        client_position="plaintiff",
        key_facts=["Contract signed", "Defendant failed to perform", "Damages quantifiable"],
        legal_theories=["Breach of contract", "Failure of consideration"]
    )
    
    print("Testing strategy simulator...")
    # assessment = simulator.assess_strategy(test_scenario)
    # print(json.dumps(assessment.to_dict(), indent=2))
