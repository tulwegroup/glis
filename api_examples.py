#!/usr/bin/env python3
"""
API Usage Examples for Ghana Legal Scraper

This script demonstrates all API endpoints with real examples.
Run the API first: python main.py api
"""

import requests
import json
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000"

class GhanaLegalAPIClient:
    """Client for Ghana Legal Scraper API"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    # ========== HEALTH & STATUS ==========

    def health_check(self) -> Dict:
        """Check API health"""
        return self._request("GET", "/health")

    def get_info(self) -> Dict:
        """Get API information"""
        return self._request("GET", "/")

    # ========== SEARCH ENDPOINTS ==========

    def basic_search(self, query: str, limit: int = 10, offset: int = 0) -> Dict:
        """
        Basic full-text search
        
        Args:
            query: Search text (required)
            limit: Results per page (1-100)
            offset: Pagination offset
        """
        params = {
            'q': query,
            'limit': limit,
            'offset': offset
        }
        return self._request("GET", "/search", params=params)

    def advanced_search(self, 
                       query: str = None,
                       year_from: int = None,
                       year_to: int = None,
                       judge: str = None,
                       statute: str = None,
                       legal_issue: str = None,
                       limit: int = 10) -> Dict:
        """
        Advanced search with filters
        
        Args:
            query: Full-text search
            year_from: Start year
            year_to: End year
            judge: Judge name
            statute: Statute/Act name
            legal_issue: Legal topic
            limit: Results per page
        """
        params = {}
        if query:
            params['q'] = query
        if year_from:
            params['year_from'] = year_from
        if year_to:
            params['year_to'] = year_to
        if judge:
            params['judge'] = judge
        if statute:
            params['statute'] = statute
        if legal_issue:
            params['legal_issue'] = legal_issue
        if limit:
            params['limit'] = limit

        return self._request("GET", "/search/advanced", params=params)

    # ========== CASE RETRIEVAL ==========

    def get_case_by_id(self, case_id: str) -> Dict:
        """Get complete case by ID"""
        return self._request("GET", f"/case/{case_id}")

    def get_case_by_citation(self, citation: str) -> Dict:
        """Get case by neutral citation"""
        # URL encode the citation
        return self._request("GET", f"/citation/{citation.replace(' ', '%20')}")

    def get_cases_by_year(self, year: int) -> Dict:
        """Get all cases from a year"""
        return self._request("GET", f"/year/{year}")

    def get_cases_by_judge(self, judge_name: str) -> Dict:
        """Get all cases where judge participated"""
        return self._request("GET", f"/judge/{judge_name.replace(' ', '%20')}")

    def get_cases_by_statute(self, statute: str) -> Dict:
        """Get all cases citing a statute"""
        return self._request("GET", f"/statute/{statute.replace(' ', '%20')}")

    # ========== STATISTICS ==========

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        return self._request("GET", "/stats")

    def get_quality_report(self) -> Dict:
        """Get quality assessment report"""
        return self._request("GET", "/quality-report")


def main():
    """Run example API calls"""
    
    # Initialize client
    client = GhanaLegalAPIClient()
    
    print("=" * 70)
    print("GHANA LEGAL SCRAPER - API EXAMPLES")
    print("=" * 70)
    print()

    try:
        # 1. Health Check
        print("1. Health Check")
        print("-" * 70)
        health = client.health_check()
        print(f"Status: {health.get('status')}")
        print(f"Database cases: {health.get('database_cases')}")
        print()

        # 2. API Info
        print("2. API Information")
        print("-" * 70)
        info = client.get_info()
        print(f"Name: {info.get('name')}")
        print(f"Version: {info.get('version')}")
        print()

        # 3. Basic Search
        print("3. Basic Full-Text Search")
        print("-" * 70)
        print("Query: property")
        try:
            results = client.basic_search("property", limit=3)
            print(f"Results found: {results.get('total')}")
            for case in results.get('results', [])[:2]:
                print(f"  - {case.get('case_name')} ({case.get('neutral_citation')})")
        except Exception as e:
            print(f"No results yet (database may be empty): {e}")
        print()

        # 4. Advanced Search
        print("4. Advanced Search (Year Range)")
        print("-" * 70)
        print("Search: Cases 2020-2023 with statute Act 29")
        try:
            results = client.advanced_search(
                year_from=2020,
                year_to=2023,
                statute="Act 29",
                limit=3
            )
            print(f"Results found: {results.get('total')}")
        except Exception as e:
            print(f"Query returned: {e}")
        print()

        # 5. Case by Citation
        print("5. Case Lookup by Citation")
        print("-" * 70)
        citation = "[2023] GHASC 45"
        print(f"Looking up: {citation}")
        try:
            case = client.get_case_by_citation(citation)
            print(f"Case: {case.get('case_name')}")
            print(f"Date: {case.get('date_decided')}")
            print(f"Quality Score: {case.get('data_quality_score')}")
        except requests.exceptions.HTTPError as e:
            print(f"Case not found (database may be empty)")
        print()

        # 6. Cases by Year
        print("6. Cases by Year")
        print("-" * 70)
        print("Cases from 2023:")
        try:
            year_cases = client.get_cases_by_year(2023)
            count = year_cases.get('total', 0)
            print(f"Found: {count} cases")
        except Exception as e:
            print(f"No cases for this year yet")
        print()

        # 7. Cases by Judge
        print("7. Cases by Judge")
        print("-" * 70)
        print("Cases by Judge: Dotse JSC")
        try:
            judge_cases = client.get_cases_by_judge("Dotse JSC")
            count = judge_cases.get('total', 0)
            print(f"Found: {count} cases")
        except Exception as e:
            print(f"No cases for this judge yet")
        print()

        # 8. Cases by Statute
        print("8. Cases by Statute")
        print("-" * 70)
        print("Cases citing: 1992 Constitution")
        try:
            statute_cases = client.get_cases_by_statute("1992 Constitution")
            count = statute_cases.get('total', 0)
            print(f"Found: {count} cases")
        except Exception as e:
            print(f"No cases citing this statute yet")
        print()

        # 9. Statistics
        print("9. Database Statistics")
        print("-" * 70)
        stats = client.get_statistics()
        
        db_stats = stats.get('database', {})
        print(f"Total cases: {db_stats.get('total_cases')}")
        print(f"Average quality: {db_stats.get('average_quality')}")
        print(f"Unique judges: {db_stats.get('unique_judges')}")
        print(f"Unique statutes: {db_stats.get('unique_statutes')}")
        print()

        # 10. Quality Report
        print("10. Quality Assessment Report")
        print("-" * 70)
        try:
            report = client.get_quality_report()
            print(f"Total cases: {report.get('total_cases')}")
            print(f"Average quality: {report.get('average_quality_score')}")
            
            by_score = report.get('cases_by_score', {})
            print("Distribution by quality score:")
            for score_range, count in by_score.items():
                print(f"  {score_range}: {count} cases")
        except Exception as e:
            print(f"No cases in database yet")
        print()

        print("=" * 70)
        print("EXAMPLES COMPLETE")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Visit http://localhost:8000/docs for interactive API docs")
        print("2. Run scraper: python main.py scrape --test")
        print("3. Check API again after scraping")
        print()

    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to API")
        print("Make sure API is running: python main.py api")
        print()


if __name__ == "__main__":
    main()
