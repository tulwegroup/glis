"""
Storage module for case data persistence
"""
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config.settings import (
    DATABASE_PATH, CASES_JSON_PATH, LOGS_DIR,
    START_YEAR, END_YEAR
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CaseStorage:
    """Manages persistence of cases to JSON and SQLite"""

    def __init__(self):
        self.db_path = DATABASE_PATH
        self.json_path = CASES_JSON_PATH
        self._init_database()
        self._load_existing_database()

    def _init_database(self):
        """Initialize SQLite database with proper schema"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE NOT NULL,
                case_name TEXT NOT NULL,
                source_url TEXT NOT NULL,
                neutral_citation TEXT NOT NULL,
                date_decided TEXT NOT NULL,
                court TEXT NOT NULL,
                disposition TEXT,
                case_summary TEXT,
                full_text TEXT,
                data_quality_score INTEGER,
                last_updated TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create judges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS judges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                judge_name TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        ''')

        # Create legal_issues table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legal_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                issue TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        ''')

        # Create statutes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                statute TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        ''')

        # Create cited_cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cited_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                cited_case TEXT NOT NULL,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        ''')

        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_case_id ON cases(case_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON cases(date_decided)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_citation ON cases(neutral_citation)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_judge ON judges(judge_name)')

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    def _load_existing_database(self):
        """Load existing case IDs to prevent duplicates"""
        self.existing_case_ids = set()
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT case_id FROM cases')
            self.existing_case_ids = {row[0] for row in cursor.fetchall()}
            conn.close()
            logger.info(f"Loaded {len(self.existing_case_ids)} existing cases")
        except Exception as e:
            logger.error(f"Error loading existing cases: {e}")
            self.existing_case_ids = set()

    def case_exists(self, case_id: str) -> bool:
        """Check if case already exists"""
        return case_id in self.existing_case_ids

    def save_case(self, case_data: Dict) -> Tuple[bool, str]:
        """
        Save case to both SQLite and JSON.
        Returns: (success, message)
        """
        try:
            case_id = case_data.get('case_id')

            # Check for duplicates
            if self.case_exists(case_id):
                return False, f"Case {case_id} already exists"

            # Save to SQLite
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO cases (
                    case_id, case_name, source_url, neutral_citation,
                    date_decided, court, disposition, case_summary,
                    full_text, data_quality_score, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case_data.get('case_id'),
                case_data.get('case_name'),
                case_data.get('source_url'),
                case_data.get('neutral_citation'),
                case_data.get('date_decided'),
                case_data.get('court', 'Supreme Court of Ghana'),
                case_data.get('disposition'),
                case_data.get('case_summary'),
                case_data.get('full_text'),
                case_data.get('data_quality_score'),
                case_data.get('last_updated', datetime.utcnow().isoformat())
            ))

            # Insert judges
            for judge in case_data.get('coram', []):
                cursor.execute(
                    'INSERT INTO judges (case_id, judge_name) VALUES (?, ?)',
                    (case_id, judge)
                )

            # Insert legal issues
            for issue in case_data.get('legal_issues', []):
                cursor.execute(
                    'INSERT INTO legal_issues (case_id, issue) VALUES (?, ?)',
                    (case_id, issue)
                )

            # Insert statutes
            for statute in case_data.get('referenced_statutes', []):
                cursor.execute(
                    'INSERT INTO statutes (case_id, statute) VALUES (?, ?)',
                    (case_id, statute)
                )

            # Insert cited cases
            for cited_case in case_data.get('cited_cases', []):
                cursor.execute(
                    'INSERT INTO cited_cases (case_id, cited_case) VALUES (?, ?)',
                    (case_id, cited_case)
                )

            conn.commit()
            conn.close()

            # Add to in-memory set
            self.existing_case_ids.add(case_id)

            # Also save to JSON for backup
            self._append_to_json(case_data)

            logger.info(f"Saved case {case_id}")
            return True, f"Case {case_id} saved successfully"

        except Exception as e:
            logger.error(f"Error saving case {case_data.get('case_id')}: {e}")
            return False, str(e)

    def _append_to_json(self, case_data: Dict):
        """Append case to JSON database file"""
        try:
            Path(self.json_path).parent.mkdir(parents=True, exist_ok=True)

            # Load existing data
            if self.json_path.exists():
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    db = json.load(f)
            else:
                db = {
                    "metadata": {
                        "total_cases": 0,
                        "last_updated": datetime.utcnow().isoformat(),
                        "coverage": f"{START_YEAR}-{END_YEAR}",
                        "data_quality_average": 0.0,
                        "version": "1.0.0"
                    },
                    "cases": [],
                    "indexes": {
                        "by_year": {},
                        "by_judge": {},
                        "by_statute": {},
                        "by_legal_issue": {}
                    }
                }

            # Add case
            db['cases'].append(case_data)
            db['metadata']['total_cases'] = len(db['cases'])
            db['metadata']['last_updated'] = datetime.utcnow().isoformat()

            # Update quality average
            quality_scores = [c.get('data_quality_score', 0) for c in db['cases']]
            if quality_scores:
                db['metadata']['data_quality_average'] = sum(quality_scores) / len(quality_scores)

            # Update indexes
            case_id = case_data.get('case_id')
            year = case_data.get('date_decided', '').split('-')[0]

            if year:
                if year not in db['indexes']['by_year']:
                    db['indexes']['by_year'][year] = []
                db['indexes']['by_year'][year].append(case_id)

            for judge in case_data.get('coram', []):
                if judge not in db['indexes']['by_judge']:
                    db['indexes']['by_judge'][judge] = []
                db['indexes']['by_judge'][judge].append(case_id)

            for statute in case_data.get('referenced_statutes', []):
                if statute not in db['indexes']['by_statute']:
                    db['indexes']['by_statute'][statute] = []
                db['indexes']['by_statute'][statute].append(case_id)

            for issue in case_data.get('legal_issues', []):
                if issue not in db['indexes']['by_legal_issue']:
                    db['indexes']['by_legal_issue'][issue] = []
                db['indexes']['by_legal_issue'][issue].append(case_id)

            # Save
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error appending to JSON: {e}")

    def get_all_cases(self, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve all cases from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = 'SELECT * FROM cases ORDER BY date_decided DESC'
            if limit:
                query += f' LIMIT {limit}'

            cursor.execute(query)
            cases = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return cases
        except Exception as e:
            logger.error(f"Error retrieving cases: {e}")
            return []

    def get_case_by_id(self, case_id: str) -> Optional[Dict]:
        """Retrieve single case by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM cases WHERE case_id = ?', (case_id,))
            case = cursor.fetchone()

            if case:
                case_dict = dict(case)

                # Get related data
                cursor.execute('SELECT judge_name FROM judges WHERE case_id = ?', (case_id,))
                case_dict['coram'] = [row[0] for row in cursor.fetchall()]

                cursor.execute('SELECT issue FROM legal_issues WHERE case_id = ?', (case_id,))
                case_dict['legal_issues'] = [row[0] for row in cursor.fetchall()]

                cursor.execute('SELECT statute FROM statutes WHERE case_id = ?', (case_id,))
                case_dict['referenced_statutes'] = [row[0] for row in cursor.fetchall()]

                cursor.execute('SELECT cited_case FROM cited_cases WHERE case_id = ?', (case_id,))
                case_dict['cited_cases'] = [row[0] for row in cursor.fetchall()]

            conn.close()
            return case_dict if case else None

        except Exception as e:
            logger.error(f"Error retrieving case {case_id}: {e}")
            return None

    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total cases
            cursor.execute('SELECT COUNT(*) FROM cases')
            total = cursor.fetchone()[0]

            # Average quality score
            cursor.execute('SELECT AVG(data_quality_score) FROM cases')
            avg_quality = cursor.fetchone()[0] or 0

            # Cases by year
            cursor.execute('''
                SELECT strftime('%Y', date_decided) as year, COUNT(*) as count
                FROM cases
                GROUP BY year
                ORDER BY year DESC
            ''')
            by_year = {row[0]: row[1] for row in cursor.fetchall()}

            # Top judges
            cursor.execute('''
                SELECT judge_name, COUNT(*) as count
                FROM judges
                GROUP BY judge_name
                ORDER BY count DESC
                LIMIT 10
            ''')
            top_judges = {row[0]: row[1] for row in cursor.fetchall()}

            conn.close()

            return {
                'total_cases': total,
                'average_quality': round(avg_quality, 2),
                'cases_by_year': by_year,
                'top_judges': top_judges,
                'last_updated': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
