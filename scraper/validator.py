"""
Validator module for case data quality checks
"""
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from config.settings import (
    MIN_TEXT_LENGTH, MIN_JUDGE_COUNT, MIN_QUALITY_SCORE,
    QUALITY_SCORE_WEIGHTS, START_YEAR, END_YEAR
)


class CaseValidator:
    """Validates extracted case data against quality standards"""

    def __init__(self):
        self.issues: List[str] = []
        self.quality_score: int = 0

    def validate_all(self, case_data: Dict) -> Tuple[bool, int, List[str]]:
        """
        Run all validation checks on case data.
        Returns: (is_valid, quality_score, issues_list)
        """
        self.issues = []
        self.quality_score = 0

        # Run all checks
        self._check_text_length(case_data.get('full_text', ''))
        self._check_citation_format(case_data.get('neutral_citation', ''))
        self._check_judge_count(case_data.get('coram', []))
        self._check_date_validity(case_data.get('date_decided', ''))
        self._check_case_id_format(case_data.get('case_id', ''))
        self._check_mandatory_fields(case_data)

        # Calculate final quality score
        self.quality_score = self._calculate_quality_score(case_data)

        is_valid = self.quality_score >= MIN_QUALITY_SCORE
        return is_valid, self.quality_score, self.issues

    def _check_text_length(self, text: str) -> bool:
        """Check if full text meets minimum length requirement"""
        if not text or len(text.strip()) < MIN_TEXT_LENGTH:
            self.issues.append(
                f"Text length too short: {len(text) if text else 0} chars "
                f"(minimum: {MIN_TEXT_LENGTH})"
            )
            return False
        return True

    def _check_citation_format(self, citation: str) -> bool:
        """Check if citation matches Ghana format: [YYYY] GHASC Number"""
        pattern = r'^\[\d{4}\] GHASC \d+$'
        if not citation or not re.match(pattern, citation):
            self.issues.append(
                f"Invalid citation format: '{citation}' "
                f"(expected: [YYYY] GHASC Number)"
            )
            return False
        return True

    def _check_judge_count(self, judges: List[str]) -> bool:
        """Check if case has minimum number of judges"""
        if not judges or len(judges) < MIN_JUDGE_COUNT:
            self.issues.append(
                f"Insufficient judges: {len(judges) if judges else 0} "
                f"(minimum: {MIN_JUDGE_COUNT})"
            )
            return False
        return True

    def _check_date_validity(self, date_str: str) -> bool:
        """Check if date is valid and within acceptable range"""
        if not date_str:
            self.issues.append("Missing date")
            return False

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            year = date_obj.year

            if year < START_YEAR or year > END_YEAR:
                self.issues.append(
                    f"Date out of range: {date_str} "
                    f"(expected: {START_YEAR}-{END_YEAR})"
                )
                return False
            return True
        except ValueError:
            self.issues.append(f"Invalid date format: {date_str} (expected: YYYY-MM-DD)")
            return False

    def _check_case_id_format(self, case_id: str) -> bool:
        """Check if case ID matches format: GHASC/YYYY/Number"""
        pattern = r'^GHASC/\d{4}/\d+$'
        if not case_id or not re.match(pattern, case_id):
            self.issues.append(
                f"Invalid case ID format: '{case_id}' "
                f"(expected: GHASC/YYYY/Number)"
            )
            return False
        return True

    def _check_mandatory_fields(self, case_data: Dict) -> bool:
        """Check if all mandatory fields are present and non-null"""
        mandatory_fields = [
            'case_id', 'source_url', 'case_name', 'neutral_citation',
            'date_decided', 'coram', 'full_text', 'disposition'
        ]

        missing = [field for field in mandatory_fields if not case_data.get(field)]
        if missing:
            self.issues.append(f"Missing mandatory fields: {', '.join(missing)}")
            return False
        return True

    def _calculate_quality_score(self, case_data: Dict) -> int:
        """
        Calculate quality score based on completion and validation.
        Score ranges from 0-100.
        """
        score = 0

        # Text length check (20 points)
        if len(case_data.get('full_text', '')) >= MIN_TEXT_LENGTH:
            score += QUALITY_SCORE_WEIGHTS['text_length']

        # Citation format check (20 points)
        if re.match(r'^\[\d{4}\] GHASC \d+$', case_data.get('neutral_citation', '')):
            score += QUALITY_SCORE_WEIGHTS['citation_format']

        # Judge count check (15 points)
        if len(case_data.get('coram', [])) >= MIN_JUDGE_COUNT:
            score += QUALITY_SCORE_WEIGHTS['judge_count']

        # Date validity check (15 points)
        try:
            date_obj = datetime.strptime(case_data.get('date_decided', ''), '%Y-%m-%d')
            if START_YEAR <= date_obj.year <= END_YEAR:
                score += QUALITY_SCORE_WEIGHTS['date_valid']
        except (ValueError, TypeError):
            pass

        # No duplicates check (15 points) - would be done during storage
        score += QUALITY_SCORE_WEIGHTS['no_duplicates']

        # Completeness check (15 points)
        mandatory_fields = ['case_id', 'source_url', 'case_name', 'date_decided', 'coram', 'full_text']
        if all(case_data.get(field) for field in mandatory_fields):
            score += QUALITY_SCORE_WEIGHTS['completeness']

        return min(score, 100)  # Cap at 100

    def extract_judges(self, judges_text: str) -> List[str]:
        """
        Extract judge names from text like "DOTSE JSC (PRESIDING), PWAMANG JSC, KULENDI JSC"
        Returns list of formatted judge names
        """
        if not judges_text:
            return []

        judges = []
        # Split by comma and process each part
        parts = judges_text.split(',')

        for part in parts:
            part = part.strip()
            # Remove "PRESIDING" and other notes
            part = re.sub(r'\s*\(.*?\)\s*', '', part)
            part = part.strip()

            if part:
                # Standardize format: First name JSC -> First Name JSC
                # Handle names like "DOTSE JSC" -> "Dotse JSC"
                words = part.split()
                if len(words) >= 2:
                    # Capitalize first word, keep title uppercase
                    formatted = ' '.join(
                        [words[0].capitalize()] + words[1:]
                    )
                    judges.append(formatted)
                elif part:
                    judges.append(part.capitalize())

        return judges

    def parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse various date formats and return ISO format YYYY-MM-DD
        Handles: "15th July, 2023", "15 July 2023", "2023-07-15", etc.
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # Already ISO format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str

        # Try common formats
        formats = [
            '%d%th %B, %Y',  # 15th July, 2023
            '%d %B %Y',      # 15 July 2023
            '%d/%m/%Y',      # 15/07/2023
            '%Y/%m/%d',      # 2023/07/15
            '%B %d, %Y',     # July 15, 2023
            '%d-%m-%Y',      # 15-07-2023
        ]

        # Remove ordinal suffix (th, st, nd, rd)
        clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

        for fmt in formats:
            try:
                dt = datetime.strptime(clean_date, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # If parsing fails, extract year and use default
        year_match = re.search(r'\b(20\d{2})\b', date_str)
        if year_match:
            year = year_match.group(1)
            return f"{year}-06-30"  # Default to June 30 if only year available

        return None

    def extract_legal_issues(self, text: str) -> List[str]:
        """Extract common legal issues from case text"""
        issues = set()

        keywords = {
            'constitutional': r'\bconstitution|fundamental rights?\b',
            'contract': r'\bcontract|agreement|terms?\b',
            'property': r'\bproperty|land|real estate|title\b',
            'succession': r'\bsuccession|inheritance|will|estate\b',
            'labour': r'\blabour|labor|employment|employment relation\b',
            'family': r'\bmarriage|divorce|custody|family\b',
            'criminal': r'\bcriminal|offense|crime|conviction\b',
            'administrative': r'\badministrative|judicial review|government\b',
            'commercial': r'\bcommercial|business|trade|company\b',
            'tort': r'\btort|negligence|damages|liability\b',
            'public': r'\bpublic law|administrative law\b',
        }

        text_lower = text.lower()
        for issue, pattern in keywords.items():
            if re.search(pattern, text_lower):
                issues.add(issue)

        return sorted(list(issues))

    def extract_statutes(self, text: str) -> List[str]:
        """Extract statute references from text"""
        statutes = set()

        # Pattern for Act references: "Act 29", "Act 123", etc.
        act_pattern = r'\bAct\s+(\d+)\b'
        for match in re.finditer(act_pattern, text, re.IGNORECASE):
            statutes.add(f"Act {match.group(1)}")

        # Pattern for Constitution
        if re.search(r'\b1992\s+Constitution\b', text, re.IGNORECASE):
            statutes.add("1992 Constitution")

        # Pattern for other common references
        common_statutes = [
            "Evidence Act 1961",
            "Criminal Code",
            "Criminal Procedure Code",
            "Civil Procedure Code",
            "Administration of Estates Act",
            "Property Rights Act",
            "Labor Act",
            "Minerals and Mining Act",
        ]

        for statute in common_statutes:
            if statute.replace(" ", "\\s+") in text or statute in text:
                statutes.add(statute)

        return sorted(list(statutes))

    def extract_case_citations(self, text: str) -> List[str]:
        """Extract previous case citations from text"""
        citations = set()

        # Pattern: [YYYY] GHASC Number or similar court citations
        pattern = r'\[\d{4}\]\s+[A-Z]{2,}\s+\d+'
        for match in re.finditer(pattern, text):
            citations.add(match.group(0))

        # Pattern: "Case v. Other [YYYY] citation"
        pattern2 = r'[A-Za-z\s,]+v\.?\s+[A-Za-z\s,]+\s+\[\d{4}\][^]]*\]'
        for match in re.finditer(pattern2, text):
            cite = match.group(0).strip()
            if cite and len(cite) < 200:  # Reasonable length
                citations.add(cite)

        return sorted(list(citations))
