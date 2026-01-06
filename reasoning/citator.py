"""
Citator & Case Authority Module - Layer 3

Determines current authority status of cases and provides alerts when precedents change.
Tracks whether cases have been overruled, affirmed, distinguished, etc.

Features:
- Case status (good law, overruled, distinguished)
- Citation tracking
- Authority scoring
- Change alerts
- Citation history
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from intelligence.citation_network import get_citation_network, CitationRelationship, CitationStatus


@dataclass
class CaseAuthority:
    """Authority status of a case"""
    case_id: str
    case_name: str
    status: str  # "good law", "overruled", "reversed", "distinguished", "bad law"
    authority_score: float  # 0-100
    last_updated: str
    is_good_law: bool
    is_overruled: bool
    is_reversed: bool
    overruling_cases: List[str]
    affirming_cases: List[str]
    distinguishing_cases: List[str]
    total_citations: int
    red_flag: bool  # True if authority questioned
    green_flag: bool  # True if strongly supported


@dataclass
class CitationAlert:
    """Alert about change in case status"""
    alert_id: str
    case_id: str
    case_name: str
    alert_type: str  # "overruled", "affirmed", "new_citation"
    date_created: str
    description: str
    severity: str  # "high", "medium", "low"


class Citator:
    """
    Citator system for tracking case authority and precedent status
    """

    def __init__(self):
        self.citation_network = get_citation_network()
        self.alerts: List[CitationAlert] = []
        self.previous_status: Dict[str, str] = {}  # Track status changes

    def get_case_authority(self, case_id: str) -> CaseAuthority:
        """
        Get current authority status of a case
        
        Args:
            case_id: Case to analyze
            
        Returns:
            CaseAuthority with current status
        """
        status = self.citation_network.get_case_status(case_id)
        
        # Determine if good law
        is_good_law = not status.is_overruled and status.current_status != "bad law"
        is_overruled = status.is_overruled
        is_reversed = len(status.overruling_cases) > 0
        
        # Determine flags
        red_flag = (status.current_status in ["overruled", "reversed", "bad law"])
        green_flag = (len(status.affirming_cases) > 3 and status.authority_score > 75)
        
        authority = CaseAuthority(
            case_id=case_id,
            case_name=case_id,  # Would need case name from database
            status=status.current_status,
            authority_score=status.authority_score,
            last_updated=datetime.now().isoformat(),
            is_good_law=is_good_law,
            is_overruled=is_overruled,
            is_reversed=is_reversed,
            overruling_cases=status.overruling_cases,
            affirming_cases=status.affirming_cases,
            distinguishing_cases=status.distinguishing_cases,
            total_citations=status.total_citations,
            red_flag=red_flag,
            green_flag=green_flag
        )
        
        return authority

    def batch_check_authority(self, case_ids: List[str]) -> Dict[str, CaseAuthority]:
        """
        Check authority of multiple cases at once
        
        Args:
            case_ids: List of case IDs
            
        Returns:
            Dict of case_id -> CaseAuthority
        """
        results = {}
        for case_id in case_ids:
            results[case_id] = self.get_case_authority(case_id)
        return results

    def flag_red_authority(self, case_id: str) -> bool:
        """
        Check if a case should be red-flagged (bad authority)
        
        Args:
            case_id: Case to check
            
        Returns:
            True if case is bad authority
        """
        authority = self.get_case_authority(case_id)
        return authority.red_flag

    def flag_green_authority(self, case_id: str) -> bool:
        """
        Check if a case should be green-flagged (strong authority)
        
        Args:
            case_id: Case to check
            
        Returns:
            True if case is strong authority
        """
        authority = self.get_case_authority(case_id)
        return authority.green_flag

    def create_alert(
        self,
        case_id: str,
        case_name: str,
        alert_type: str,
        description: str,
        severity: str = "medium"
    ) -> CitationAlert:
        """
        Create an alert about case status change
        
        Args:
            case_id: Case affected
            case_name: Case name
            alert_type: Type of alert (overruled, affirmed, etc.)
            description: Alert description
            severity: Severity level
            
        Returns:
            CitationAlert created
        """
        alert = CitationAlert(
            alert_id=f"{case_id}_{datetime.now().isoformat()}",
            case_id=case_id,
            case_name=case_name,
            alert_type=alert_type,
            date_created=datetime.now().isoformat(),
            description=description,
            severity=severity
        )
        
        self.alerts.append(alert)
        return alert

    def check_for_changes(self, case_id: str) -> List[CitationAlert]:
        """
        Check if case status has changed since last check
        
        Args:
            case_id: Case to check
            
        Returns:
            List of new alerts if status changed
        """
        current_authority = self.get_case_authority(case_id)
        previous = self.previous_status.get(case_id)
        
        new_alerts = []
        
        # Check for status change
        if previous and previous != current_authority.status:
            alert = self.create_alert(
                case_id=case_id,
                case_name=current_authority.case_name,
                alert_type="status_change",
                description=f"Status changed from {previous} to {current_authority.status}",
                severity="high" if current_authority.red_flag else "medium"
            )
            new_alerts.append(alert)
        
        # Check for new overruling cases
        if previous:
            prev_status = self.citation_network.get_case_status(case_id)
            if len(current_authority.overruling_cases) > len(prev_status.overruling_cases):
                alert = self.create_alert(
                    case_id=case_id,
                    case_name=current_authority.case_name,
                    alert_type="overruled",
                    description=f"Case has been overruled by {current_authority.overruling_cases[-1]}",
                    severity="high"
                )
                new_alerts.append(alert)
        
        # Update previous status
        self.previous_status[case_id] = current_authority.status
        
        return new_alerts

    def get_citation_history(self, case_id: str) -> List[Dict]:
        """
        Get chronological history of citations to a case
        
        Args:
            case_id: Case to trace
            
        Returns:
            List of citation events in chronological order
        """
        citing = self.citation_network.find_citing_cases(case_id)
        
        history = []
        for rel_type, cases in citing.items():
            for citing_case in cases:
                history.append({
                    "cited_case": case_id,
                    "citing_case": citing_case,
                    "relationship": rel_type.value,
                })
        
        return sorted(history, key=lambda x: x['cited_case'])

    def validate_authority_before_citing(
        self,
        cited_cases: List[str],
        case_name: str
    ) -> Dict[str, Dict]:
        """
        Validate authority of all cases before citing them
        Useful for drafting pleadings or research notes
        
        Args:
            cited_cases: Cases you want to cite
            case_name: Name of current case/project
            
        Returns:
            Dict of case_id -> authority info and warnings
        """
        validation = {}
        
        for case_id in cited_cases:
            authority = self.get_case_authority(case_id)
            
            warnings = []
            if authority.red_flag:
                warnings.append("⚠ RED FLAG: Case authority is questioned")
            
            if authority.is_reversed:
                warnings.append("⚠ Case has been reversed")
            
            if authority.is_overruled:
                warnings.append("⚠ Case has been overruled - DO NOT CITE")
            
            if not authority.affirming_cases:
                warnings.append("⚠ Case has few supporting citations")
            
            validation[case_id] = {
                "case_name": authority.case_name,
                "status": authority.status,
                "is_good_law": authority.is_good_law,
                "authority_score": authority.authority_score,
                "warnings": warnings,
                "can_cite": authority.is_good_law,
                "color_code": "🟢" if authority.green_flag else ("🔴" if authority.red_flag else "🟡"),
            }
        
        return validation

    def get_alerts(self, severity: Optional[str] = None) -> List[CitationAlert]:
        """
        Get all alerts, optionally filtered by severity
        
        Args:
            severity: Optional severity filter ("high", "medium", "low")
            
        Returns:
            List of CitationAlerts
        """
        if severity:
            return [a for a in self.alerts if a.severity == severity]
        return self.alerts

    def clear_old_alerts(self, days: int = 30):
        """
        Clear alerts older than specified days
        
        Args:
            days: Keep alerts from last N days
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        self.alerts = [a for a in self.alerts if datetime.fromisoformat(a.date_created) > cutoff]

    def get_statistics(self) -> Dict:
        """Get statistics about citation network and authority tracking"""
        return {
            "total_alerts": len(self.alerts),
            "high_severity_alerts": len([a for a in self.alerts if a.severity == "high"]),
            "total_status_tracked": len(self.previous_status),
            "network_stats": self.citation_network.get_network_stats(),
        }


# Global citator instance
_citator = None


def get_citator() -> Citator:
    """Get or create global citator instance"""
    global _citator
    if _citator is None:
        _citator = Citator()
    return _citator
