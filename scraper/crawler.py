"""
Main crawler module for Ghana Legal Scraper
Orchestrates the scraping, parsing, validation, and storage pipeline
"""
import time
import logging
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
from urllib.robotparser import RobotFileParser

from config.settings import (
    BASE_URL, SUPREME_COURT_LIST, ROBOTS_TXT_URL, REQUEST_DELAY,
    MAX_RETRIES, BACKOFF_FACTOR, USER_AGENT, SCRAPED_URLS_LOG,
    ERRORS_LOG, START_YEAR, END_YEAR, MIN_QUALITY_SCORE,
    STATS_DIR, TARGET_CASES, MIN_AVERAGE_QUALITY
)
from scraper.parser import CaseParser, PDFParser
from scraper.validator import CaseValidator
from scraper.storage import CaseStorage


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(ERRORS_LOG),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GhanaLegalCrawler:
    """
    Main crawler for Ghana Supreme Court cases
    Manages the entire pipeline: discovery, scraping, parsing, validation, storage
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.robot_parser = RobotFileParser()
        self.case_parser = CaseParser()
        self.pdf_parser = PDFParser()
        self.validator = CaseValidator()
        self.case_parser.validator = self.validator  # Inject validator
        self.storage = CaseStorage()
        self.scraped_urls: List[str] = []
        self.errors: List[Dict] = []
        self.stats = {
            'total_attempted': 0,
            'total_scraped': 0,
            'total_valid': 0,
            'total_errors': 0,
            'start_time': None,
            'end_time': None,
        }

    def check_robots_txt(self):
        """Check robots.txt compliance"""
        try:
            self.robot_parser.set_url(ROBOTS_TXT_URL)
            self.robot_parser.read()
            logger.info("Robots.txt loaded successfully")
            return True
        except Exception as e:
            logger.warning(f"Could not load robots.txt: {e}. Proceeding with caution.")
            return False

    def can_fetch(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        try:
            path = url.replace(BASE_URL, '')
            return self.robot_parser.can_fetch(USER_AGENT, path)
        except:
            # If robot parser not loaded, allow by default
            return True

    def fetch_url(self, url: str, max_retries: int = MAX_RETRIES) -> Optional[str]:
        """
        Fetch URL content with retry logic and rate limiting
        """
        # Check robots.txt
        if not self.can_fetch(url):
            logger.warning(f"Robots.txt disallows: {url}")
            return None

        # Rate limiting
        time.sleep(REQUEST_DELAY)

        retries = 0
        while retries < max_retries:
            try:
                response = self.session.get(url, timeout=10)

                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = 60 * (2 ** retries)  # Exponential backoff
                    logger.warning(
                        f"Rate limited. Waiting {wait_time} seconds before retry..."
                    )
                    time.sleep(wait_time)
                    retries += 1
                    continue

                # Handle other errors
                if response.status_code == 404:
                    logger.warning(f"Page not found: {url}")
                    self._log_error(url, 'HTTP_404', 'Page not found')
                    return None

                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code}: {url}")
                    retries += 1
                    continue

                # Log successful fetch
                self.scraped_urls.append(url)
                logger.info(f"Successfully fetched: {url}")
                return response.text

            except requests.RequestException as e:
                logger.warning(f"Request failed for {url}: {e}")
                retries += 1
                wait_time = REQUEST_DELAY * (BACKOFF_FACTOR ** retries)
                time.sleep(wait_time)

        self._log_error(url, 'REQUEST_FAILED', 'Max retries exceeded')
        return None

    def scrape_case_list(self) -> List[Dict]:
        """
        Scrape list of Supreme Court cases from GhanaLII
        Returns list of case metadata and URLs
        """
        logger.info("Starting case discovery phase...")

        all_cases = []

        # Scrape judgments for each year
        for year in range(START_YEAR, END_YEAR + 1):
            list_url = f"{SUPREME_COURT_LIST}?year={year}"
            logger.info(f"Scraping cases for year {year}...")

            html = self.fetch_url(list_url)
            if not html:
                continue

            cases = self.case_parser.parse_judgment_list_page(html)
            all_cases.extend(cases)

            logger.info(f"Found {len(cases)} cases for year {year}")

        logger.info(f"Total cases discovered: {len(all_cases)}")
        return all_cases

    def process_case(self, case_url: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Process a single case:
        1. Fetch the page
        2. Parse content
        3. Validate data
        4. Save if valid
        
        Returns: (success, case_data, message)
        """
        self.stats['total_attempted'] += 1

        # Fetch case page
        html = self.fetch_url(case_url)
        if not html:
            return False, None, "Failed to fetch page"

        # Parse case
        case_data = self.case_parser.parse_case_page(html, case_url)
        if not case_data:
            return False, None, "Failed to parse case"

        self.stats['total_scraped'] += 1

        # Validate case
        is_valid, quality_score, issues = self.validator.validate_all(case_data)
        case_data['data_quality_score'] = quality_score

        if not is_valid:
            issue_str = "; ".join(issues)
            logger.warning(
                f"Case validation failed [{case_data.get('case_id')}]: {issue_str}"
            )
            self._log_error(
                case_url, 'VALIDATION_FAILED',
                f"Quality score {quality_score}: {issue_str}"
            )
            return False, case_data, f"Validation failed: {issue_str}"

        self.stats['total_valid'] += 1

        # Check for duplicates
        if self.storage.case_exists(case_data.get('case_id')):
            return False, case_data, "Case already in database"

        # Save case
        success, message = self.storage.save_case(case_data)
        if success:
            logger.info(f"Saved: {case_data.get('case_id')} (Quality: {quality_score})")
        else:
            self._log_error(case_url, 'STORAGE_ERROR', message)

        return success, case_data, message

    def run_scraping_campaign(self, test_mode: bool = False) -> Dict:
        """
        Execute complete scraping campaign
        
        Args:
            test_mode: If True, only scrape 10 cases for testing
        
        Returns: Statistics dictionary
        """
        self.stats['start_time'] = datetime.utcnow()
        logger.info("=" * 60)
        logger.info("GHANA LEGAL SCRAPER - CAMPAIGN START")
        logger.info("=" * 60)

        # Check robots.txt
        self.check_robots_txt()

        # Phase 1: Discovery
        logger.info("\n[PHASE 1] DISCOVERY - Finding all case URLs")
        case_list = self.scrape_case_list()

        if not case_list:
            logger.error("No cases found. Aborting.")
            return self.stats

        logger.info(f"Found {len(case_list)} cases to process")

        # Phase 2: Processing
        logger.info("\n[PHASE 2] PROCESSING - Scraping and validating cases")

        limit = 10 if test_mode else len(case_list)
        for i, case in enumerate(case_list[:limit], 1):
            logger.info(f"\n[{i}/{limit}] Processing: {case.get('title')}")

            success, case_data, message = self.process_case(case['full_url'])
            if success:
                logger.info(f"✓ Success: {message}")
            else:
                logger.warning(f"✗ Failed: {message}")

            # Progress logging every 10 cases
            if i % 10 == 0:
                self._save_daily_stats()

        self.stats['end_time'] = datetime.utcnow()

        # Phase 3: Reporting
        logger.info("\n[PHASE 3] REPORTING - Generating statistics")
        self._generate_report()

        logger.info("\n" + "=" * 60)
        logger.info("CAMPAIGN COMPLETE")
        logger.info("=" * 60)

        return self.stats

    def _log_error(self, url: str, error_type: str, message: str):
        """Log error details"""
        error = {
            'timestamp': datetime.utcnow().isoformat(),
            'url': url,
            'error_type': error_type,
            'message': message
        }
        self.errors.append(error)
        self.stats['total_errors'] += 1

    def _save_daily_stats(self):
        """Save progress statistics to file"""
        try:
            stats_file = STATS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}_stats.json"

            elapsed = (datetime.utcnow() - self.stats['start_time']).total_seconds()
            rate = self.stats['total_valid'] / elapsed if elapsed > 0 else 0

            daily_stats = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'target': TARGET_CASES,
                'scraped_today': self.stats['total_valid'],
                'total_scraped': self.stats['total_valid'],
                'success_rate': (self.stats['total_valid'] / self.stats['total_attempted'] * 100) if self.stats['total_attempted'] > 0 else 0,
                'average_quality_score': 0,  # Will be calculated from storage
                'errors_encountered': self.stats['total_errors'],
                'cases_per_hour': rate * 3600,
                'estimated_completion': self._estimate_completion()
            }

            with open(stats_file, 'w') as f:
                json.dump(daily_stats, f, indent=2)

            logger.info(f"Saved daily stats: {stats_file}")

        except Exception as e:
            logger.error(f"Error saving stats: {e}")

    def _estimate_completion(self) -> str:
        """Estimate completion date based on current progress"""
        if self.stats['total_attempted'] == 0:
            return "Unknown"

        success_rate = self.stats['total_valid'] / self.stats['total_attempted']
        remaining = TARGET_CASES - self.stats['total_valid']

        if success_rate == 0:
            return "Unknown"

        elapsed = (datetime.utcnow() - self.stats['start_time']).total_seconds()
        cases_per_second = self.stats['total_valid'] / elapsed if elapsed > 0 else 0

        if cases_per_second == 0:
            return "Unknown"

        remaining_seconds = remaining / cases_per_second
        completion_date = datetime.utcnow() + timedelta(seconds=remaining_seconds)

        return completion_date.strftime('%Y-%m-%d')

    def _generate_report(self):
        """Generate final quality and statistics report"""
        try:
            stats = self.storage.get_stats()

            report = {
                'title': 'Ghana Legal Scraper - Quality Report',
                'date': datetime.utcnow().isoformat(),
                'summary': {
                    'total_cases': stats.get('total_cases', 0),
                    'average_quality': stats.get('average_quality', 0),
                    'target': TARGET_CASES,
                    'target_met': stats.get('total_cases', 0) >= TARGET_CASES,
                    'quality_target_met': stats.get('average_quality', 0) >= MIN_AVERAGE_QUALITY
                },
                'scraping_stats': {
                    'total_attempted': self.stats['total_attempted'],
                    'total_scraped': self.stats['total_scraped'],
                    'total_valid': self.stats['total_valid'],
                    'total_errors': self.stats['total_errors'],
                    'success_rate': (self.stats['total_valid'] / self.stats['total_attempted'] * 100) if self.stats['total_attempted'] > 0 else 0
                },
                'data_breakdown': {
                    'cases_by_year': stats.get('cases_by_year', {}),
                    'top_judges': stats.get('top_judges', {})
                },
                'errors': self.errors[:10]  # Last 10 errors
            }

            report_file = STATS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Report saved: {report_file}")
            logger.info(f"Total cases: {stats.get('total_cases', 0)}")
            logger.info(f"Average quality: {stats.get('average_quality', 0):.2f}")

            return report

        except Exception as e:
            logger.error(f"Error generating report: {e}")

    def save_scraped_urls(self):
        """Save all scraped URLs to log file"""
        try:
            with open(SCRAPED_URLS_LOG, 'w') as f:
                for url in self.scraped_urls:
                    f.write(f"{datetime.utcnow().isoformat()} - {url}\n")
            logger.info(f"Saved {len(self.scraped_urls)} URLs to log")
        except Exception as e:
            logger.error(f"Error saving URLs log: {e}")
