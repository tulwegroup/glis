"""
Search functionality for Ghana Legal Database
"""
import sqlite3
import json
from typing import List, Optional, Dict
from pathlib import Path
from config.settings import DATABASE_PATH, CASES_JSON_PATH
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CaseSearchEngine:
    """Full-text and advanced search for cases"""

    def __init__(self):
        self.db_path = DATABASE_PATH
        self.json_path = CASES_JSON_PATH
        self.cases_db = self._load_json_db()

    def _load_json_db(self) -> Dict:
        """Load cases from JSON file for in-memory search"""
        try:
            if self.json_path.exists():
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON database: {e}")

        return {
            'metadata': {},
            'cases': [],
            'indexes': {}
        }

    def basic_search(self, query: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        Basic full-text search across case names, summaries, and text.
        """
        if not query:
            return []

        query_lower = query.lower()
        results = []

        for case in self.cases_db.get('cases', []):
            # Search in case name
            if query_lower in case.get('case_name', '').lower():
                results.append((case, 1.0))  # Perfect match in name
                continue

            # Search in summary
            if query_lower in case.get('case_summary', '').lower():
                results.append((case, 0.8))
                continue

            # Search in full text (with lower relevance)
            if query_lower in case.get('full_text', '').lower():
                results.append((case, 0.5))

        # Sort by relevance
        results.sort(key=lambda x: x[1], reverse=True)

        # Return paginated results
        cases = [r[0] for r in results]
        return cases[offset:offset + limit]

    def advanced_search(
        self,
        query: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        judge: Optional[str] = None,
        statute: Optional[str] = None,
        legal_issue: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """
        Advanced search with multiple filters
        """
        results = []

        for case in self.cases_db.get('cases', []):
            match = True

            # Filter by year range
            if year_from or year_to:
                try:
                    case_year = int(case.get('date_decided', '')[:4])
                    if year_from and case_year < year_from:
                        match = False
                    if year_to and case_year > year_to:
                        match = False
                except:
                    match = False

            # Filter by judge
            if match and judge:
                judge_found = any(
                    judge.lower() in j.lower()
                    for j in case.get('coram', [])
                )
                if not judge_found:
                    match = False

            # Filter by statute
            if match and statute:
                statute_found = any(
                    statute.lower() in s.lower()
                    for s in case.get('referenced_statutes', [])
                )
                if not statute_found:
                    match = False

            # Filter by legal issue
            if match and legal_issue:
                issue_found = any(
                    legal_issue.lower() in i.lower()
                    for i in case.get('legal_issues', [])
                )
                if not issue_found:
                    match = False

            # Text search in remaining results
            if match and query:
                query_lower = query.lower()
                text_match = (
                    query_lower in case.get('case_name', '').lower() or
                    query_lower in case.get('case_summary', '').lower() or
                    query_lower in case.get('full_text', '').lower()
                )
                if not text_match:
                    match = False

            if match:
                results.append(case)

        # Return paginated results
        return results[offset:offset + limit]

    def citation_lookup(self, citation: str) -> Optional[Dict]:
        """
        Look up a case by neutral citation [YYYY] GHASC Number
        """
        citation = citation.strip()

        # Try exact match first
        for case in self.cases_db.get('cases', []):
            if case.get('neutral_citation') == citation:
                return case

        # Try case_id
        case_id = self._citation_to_case_id(citation)
        if case_id:
            for case in self.cases_db.get('cases', []):
                if case.get('case_id') == case_id:
                    return case

        return None

    def _citation_to_case_id(self, citation: str) -> Optional[str]:
        """Convert citation to case ID"""
        import re
        pattern = r'\[(\d{4})\]\s+GHASC\s+(\d+)'
        match = re.search(pattern, citation)

        if match:
            year = match.group(1)
            number = match.group(2)
            return f"GHASC/{year}/{number}"

        return None

    def search_by_year(self, year: int) -> List[Dict]:
        """Get all cases from a specific year"""
        year_str = str(year)
        year_index = self.cases_db.get('indexes', {}).get('by_year', {})

        case_ids = year_index.get(year_str, [])
        results = []

        for case in self.cases_db.get('cases', []):
            if case.get('case_id') in case_ids:
                results.append(case)

        return results

    def search_by_judge(self, judge_name: str) -> List[Dict]:
        """Get all cases where judge participated"""
        results = []
        judge_lower = judge_name.lower()

        for case in self.cases_db.get('cases', []):
            judge_found = any(
                judge_lower in j.lower()
                for j in case.get('coram', [])
            )
            if judge_found:
                results.append(case)

        return results

    def search_by_statute(self, statute: str) -> List[Dict]:
        """Get all cases citing a particular statute"""
        results = []
        statute_lower = statute.lower()

        for case in self.cases_db.get('cases', []):
            statute_found = any(
                statute_lower in s.lower()
                for s in case.get('referenced_statutes', [])
            )
            if statute_found:
                results.append(case)

        return results

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        cases = self.cases_db.get('cases', [])
        metadata = self.cases_db.get('metadata', {})

        stats = {
            'total_cases': len(cases),
            'average_quality': metadata.get('data_quality_average', 0),
            'years_covered': metadata.get('coverage', 'Unknown'),
            'last_updated': metadata.get('last_updated', 'Unknown'),
            'version': metadata.get('version', '1.0.0')
        }

        if cases:
            # Calculate additional stats
            years = set()
            judges = set()
            statutes = set()
            issues = set()

            for case in cases:
                try:
                    year = case.get('date_decided', '')[:4]
                    if year:
                        years.add(year)
                except:
                    pass

                judges.update(case.get('coram', []))
                statutes.update(case.get('referenced_statutes', []))
                issues.update(case.get('legal_issues', []))

            stats['unique_years'] = len(years)
            stats['unique_judges'] = len(judges)
            stats['unique_statutes'] = len(statutes)
            stats['unique_issues'] = len(issues)

        return stats

    def refresh_from_db(self):
        """Refresh in-memory database from file"""
        self.cases_db = self._load_json_db()
        logger.info("Refreshed search database")
