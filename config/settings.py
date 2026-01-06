"""
Configuration and settings for Ghana Legal Scraper
"""
import os
from pathlib import Path
from typing import List

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = DATA_DIR / "logs"
STATS_DIR = DATA_DIR / "stats"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR, STATS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Web scraping settings
BASE_URL = "https://ghalii.org"
SEARCH_PARAMS = "?type=judgment&court=supreme_court&year=2000-2024"
ROBOTS_TXT_URL = f"{BASE_URL}/robots.txt"
SUPREME_COURT_LIST = f"{BASE_URL}/judgment/court/supreme_court"

# Rate limiting (in seconds)
REQUEST_DELAY = 5  # 1 request per 5 seconds
MAX_RETRIES = 3
BACKOFF_FACTOR = 2.0

# User Agent
USER_AGENT = "GLIS-Legal-Research-Bot/1.0 (+https://legalai.gh)"

# Data quality thresholds
MIN_TEXT_LENGTH = 500  # Minimum characters for full text
MIN_JUDGE_COUNT = 3    # Minimum judges for Supreme Court
MIN_QUALITY_SCORE = 60  # Reject if below this score

# Quality score weights
QUALITY_SCORE_WEIGHTS = {
    "text_length": 20,      # Has >500 chars
    "citation_format": 20,  # Valid citation format
    "judge_count": 15,      # Has 3+ judges
    "date_valid": 15,       # Valid date range
    "no_duplicates": 15,    # Not a duplicate
    "completeness": 15      # All mandatory fields
}

# Database settings
DATABASE_PATH = PROCESSED_DATA_DIR / "ghasc_cases.db"
CASES_JSON_PATH = PROCESSED_DATA_DIR / "cases.json"

# Logging settings
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SCRAPED_URLS_LOG = LOGS_DIR / "scraped_urls.log"
ERRORS_LOG = LOGS_DIR / "errors.log"
QUALITY_REPORT_LOG = LOGS_DIR / "quality_report.log"

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
API_DEBUG = True

# Year range for scraping
START_YEAR = 2000
END_YEAR = 2024

# Target metrics
TARGET_CASES = 500
MIN_AVERAGE_QUALITY = 85

# Ghana-specific legal titles
GHANA_LEGAL_TITLES = [
    "JSC",   # Justice of Supreme Court
    "JA",    # Justice of Appeal
    "J",     # Judge
    "C.J",   # Chief Justice
]

# Common Ghana statutes and acts for reference
GHANA_KEY_LEGISLATION = [
    "Act 29",
    "1992 Constitution",
    "Evidence Act 1961",
    "Criminal Code",
    "Criminal Procedure Code",
    "Civil Procedure Code",
    "Administration of Estates Act",
    "Property Rights Act",
    "Labor Act",
    "Minerals and Mining Act",
]

# Test cases for validation
TEST_CASES = [
    {
        "name": "THE REPUBLIC v. HIGH COURT (COMMERCIAL DIVISION), ACCRA; EX PARTE ATTORNEY-GENERAL",
        "citation": "[2019] GHASC 41",
        "year": 2019,
    },
    {
        "name": "AKUFO-ADDO v. ELECTORAL COMMISSION & ANOR",
        "citation": "[2020] GHASC 6",
        "year": 2020,
    },
    {
        "name": "MARGARET BANFUL & ORS v. LAND COMMISSION & ORS",
        "citation": "[2022] GHASC 12",
        "year": 2022,
    },
]
