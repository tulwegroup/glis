"""
Parser module for HTML/PDF content extraction
"""
import re
import logging
from typing import Dict, Optional, List
from datetime import datetime
from html import unescape


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CaseParser:
    """Parses HTML/PDF judgment content and extracts structured data"""

    def __init__(self, validator=None):
        self.validator = validator

    def parse_case_page(self, html_content: str, source_url: str) -> Optional[Dict]:
        """
        Parse a complete case judgment page.
        Handles both direct judgment text and PDF links.
        """
        if not html_content:
            logger.warning(f"Empty content for {source_url}")
            return None

        case_data = {
            'source_url': source_url,
            'last_updated': datetime.utcnow().isoformat()
        }

        try:
            # Extract case name
            case_data['case_name'] = self._extract_case_name(html_content)

            # Extract neutral citation
            case_data['neutral_citation'] = self._extract_citation(html_content)

            # Extract case ID from citation
            if case_data.get('neutral_citation'):
                case_data['case_id'] = self._citation_to_case_id(
                    case_data['neutral_citation']
                )

            # Extract date decided
            case_data['date_decided'] = self._extract_date(html_content)

            # Extract judges/coram
            case_data['coram'] = self._extract_judges(html_content)

            # Extract disposition
            case_data['disposition'] = self._extract_disposition(html_content)

            # Extract full text
            full_text = self._extract_full_text(html_content)
            case_data['full_text'] = full_text
            case_data['case_summary'] = full_text[:200] if full_text else ""

            # Extract legal issues, statutes, and citations
            if self.validator:
                case_data['legal_issues'] = self.validator.extract_legal_issues(full_text)
                case_data['referenced_statutes'] = self.validator.extract_statutes(full_text)
                case_data['cited_cases'] = self.validator.extract_case_citations(full_text)
            else:
                case_data['legal_issues'] = []
                case_data['referenced_statutes'] = []
                case_data['cited_cases'] = []

            case_data['court'] = 'Supreme Court of Ghana'

            # Set placeholder quality score (will be calculated by validator)
            case_data['data_quality_score'] = 0

            return case_data

        except Exception as e:
            logger.error(f"Error parsing case from {source_url}: {e}")
            return None

    def _extract_case_name(self, html: str) -> Optional[str]:
        """
        Extract case name/title from HTML.
        Looks for common patterns in legal document structure.
        """
        # Try to find case name in common HTML patterns
        patterns = [
            r'<h1[^>]*>([^<]+)</h1>',
            r'<title>([^<]+)</title>',
            r'<div class="case-name">([^<]+)</div>',
            r'<div class="title">([^<]+)</div>',
            r'<strong>([A-Z][^<]+?vs\.?[^<]+?)</strong>',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                name = unescape(match.group(1)).strip()
                # Standardize format
                name = self._standardize_case_name(name)
                if name and len(name) > 5:
                    return name

        return None

    def _standardize_case_name(self, name: str) -> str:
        """Standardize case name format"""
        # Convert to uppercase
        name = name.upper().strip()

        # Standardize "v." to "vs."
        name = re.sub(r'\bv\.?\s+', ' vs. ', name)

        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name)

        return name

    def _extract_citation(self, html: str) -> Optional[str]:
        """
        Extract neutral citation [YYYY] GHASC Number
        """
        pattern = r'\[(\d{4})\]\s+GHASC\s+(\d+)'
        match = re.search(pattern, html)

        if match:
            year = match.group(1)
            number = match.group(2)
            return f"[{year}] GHASC {number}"

        return None

    def _citation_to_case_id(self, citation: str) -> Optional[str]:
        """Convert citation to case ID format GHASC/YYYY/Number"""
        pattern = r'\[(\d{4})\]\s+GHASC\s+(\d+)'
        match = re.search(pattern, citation)

        if match:
            year = match.group(1)
            number = match.group(2)
            return f"GHASC/{year}/{number}"

        return None

    def _extract_date(self, html: str) -> Optional[str]:
        """
        Extract judgment date and convert to ISO format
        """
        # Common patterns for dates in legal documents
        patterns = [
            r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*.?\s+\d{4})',
            r'Date of judgment:\s*([^<\n]+)',
            r'Judgment date:\s*([^<\n]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                if self.validator:
                    parsed_date = self.validator.parse_date(date_str)
                    if parsed_date:
                        return parsed_date

        return None

    def _extract_judges(self, html: str) -> List[str]:
        """
        Extract list of judges from coram section
        """
        # Pattern for judge lists
        patterns = [
            r'CORAM\s*:?([^<]+?)(?:</[^>]+>|$)',
            r'<div class="coram">([^<]+)</div>',
            r'judges?:\s*([^<]+?)(?:</[^>]+>|$)',
        ]

        judges_text = None
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                judges_text = match.group(1)
                break

        if judges_text and self.validator:
            return self.validator.extract_judges(judges_text)

        # Fallback: extract any names with JSC or JA titles
        judge_pattern = r'([A-Z][a-z\s]+?(?:JSC|JA|J)\b)'
        matches = re.findall(judge_pattern, html)
        if matches:
            if self.validator:
                return self.validator.extract_judges(', '.join(matches))
            return [j.strip() for j in matches if j.strip()]

        return []

    def _extract_disposition(self, html: str) -> Optional[str]:
        """
        Extract case disposition (Appeal allowed, dismissed, etc.)
        """
        patterns = [
            r'(?:Appeal|Application|Petition)\s+(?:is\s+)?(?:allowed|dismissed|granted|denied|refused)',
            r'(?:held|decided|ruled)\s+(?:that\s+)?([^.]+)',
            r'DISPOSITION:\s*([^<]+)',
            r'Decision:\s*([^<]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                disposition = unescape(match.group(1) if match.lastindex else match.group(0))
                disposition = disposition.strip()
                if disposition and len(disposition) < 200:
                    return disposition

        return None

    def _extract_full_text(self, html: str) -> Optional[str]:
        """
        Extract full judgment text from HTML
        Removes HTML tags and formatting
        """
        # Remove script and style elements
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML comments
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

        # Remove other HTML tags
        text = re.sub(r'<[^>]+>', '\n', text)

        # Decode HTML entities
        text = unescape(text)

        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        # Clean up
        text = text.strip()

        # Ensure minimum length
        if len(text) < 100:
            return None

        return text

    def parse_judgment_list_page(self, html: str) -> List[Dict]:
        """
        Parse a list page of judgments and extract case links
        Returns list of case metadata and URLs
        """
        cases = []

        # Pattern for case links: find table rows or list items with case info
        # Adjust based on actual GhanaLII structure
        patterns = [
            r'<a href="([^"]+)"[^>]*>([^<]+)</a>',
            r'<tr[^>]*>.*?<a href="([^"]+)"[^>]*>([^<]+)</a>',
        ]

        # Extract links and case names
        links = re.findall(r'href="(/judgment/[^"]+)"[^>]*>([^<]+)</a>', html)

        for link, title in links:
            case = {
                'title': unescape(title).strip(),
                'relative_url': link,
                'full_url': 'https://ghalii.org' + link if link.startswith('/') else link
            }
            cases.append(case)

        logger.info(f"Extracted {len(cases)} cases from list page")
        return cases


class PDFParser:
    """
    Handles PDF extraction if needed
    For now, returns placeholder - would integrate with PyPDF2 or pdfplumber
    """

    def __init__(self):
        self.parser = CaseParser()

    def extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        """
        Extract text from PDF content
        Placeholder - would use pdfplumber or PyPDF2
        """
        logger.warning("PDF parsing not yet implemented. Falling back to HTML parsing.")
        return None
